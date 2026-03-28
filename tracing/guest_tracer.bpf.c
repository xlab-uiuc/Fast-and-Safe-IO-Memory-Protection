#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#include "tracing_utils.h"

char LICENSE[] SEC("license") = "GPL";

#define SAMPLE_RATE_POW2 1024
#define SAMPLE_MASK (SAMPLE_RATE_POW2 - 1)

struct task_trace_data_t {
    u64 start_times[TRACE_FUNCS_END];
};

struct {
    __uint(type, BPF_MAP_TYPE_TASK_STORAGE);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, int);
    __type(value, struct task_trace_data_t);
} task_storage SEC(".maps");

struct
{
  __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
  __type(key, u32);
  __type(value, struct latency_stats_t);
  __uint(max_entries, FUNCTION_NAME_MAX);
} func_latency_stats SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, TRACE_FUNCS_END * HISTO_BUCKETS); 
    __type(key, u32);
    __type(value, u64);
} latency_histogram SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, u32);
    __type(value, u64);
    __uint(max_entries, FUNCTION_NAME_MAX);
} func_call_counts SEC(".maps");

static __always_inline u32 log2_u64(u64 v)
{
    u32 r = 0;
    if (v > 0xFFFFFFFF) { v >>= 32; r += 32; }
    if (v > 0xFFFF)     { v >>= 16; r += 16; }
    if (v > 0xFF)       { v >>= 8;  r += 8; }
    if (v > 0xF)        { v >>= 4;  r += 4; }
    if (v > 0x3)        { v >>= 2;  r += 2; }
    if (v > 0x1)        { r += 1; }
    return r;
}

static __always_inline int
_bpf_utils_trace_func_entry(struct pt_regs *ctx)
{
  u64 cookie = bpf_get_attach_cookie(ctx);

  if (cookie >= TRACE_FUNCS_END) {
    return 0;
  }

  struct task_struct *task = bpf_get_current_task_btf();
  struct task_trace_data_t *data = bpf_task_storage_get(&task_storage, task, 0, BPF_LOCAL_STORAGE_GET_F_CREATE);
  
  if (!data)
      return 0;

  data->start_times[cookie] = bpf_ktime_get_ns();
  return 0;
}

static __always_inline int
_bpf_utils_trace_func_exit(struct pt_regs *ctx, enum Domain domain, bool is_uprobe)
{
  u64 cookie = bpf_get_attach_cookie(ctx);

  if (cookie >= TRACE_FUNCS_END) {
    u32 func_enum_key = (u32)cookie;
    u64 *count = bpf_map_lookup_elem(&func_call_counts, &func_enum_key);
    if (count) {
      __sync_fetch_and_add(count, 1);
    }

    return 0;
  }

  struct task_struct *task = bpf_get_current_task_btf();
  struct task_trace_data_t *data = bpf_task_storage_get(&task_storage, task, 0, 0);

  if (!data)
      return 0;

  u64 start_ts = data->start_times[cookie];
  if (start_ts == 0)
      return 0;

  // Clear it (optional, but good practice)
  data->start_times[cookie] = 0;

  u64 duration_ns;
  u64 duration_us;
  u32 func_enum_key;

  duration_ns = bpf_ktime_get_ns() - start_ts;
  func_enum_key = (u32)cookie;

  // Sanity check: if duration is larger than 1 second, it's likely a stale entry
  // or something went wrong.
  // if (duration_ns > 1000000000ULL) {
  //     return 0;
  // }

  struct latency_stats_t *stats = bpf_map_lookup_elem(&func_latency_stats, &func_enum_key);
  if (stats) {
    __sync_fetch_and_add(&stats->count, 1);
    __sync_fetch_and_add(&stats->total_duration_ns, duration_ns);
    
    // Convert duration to microseconds for sum of squares to prevent overflow
    duration_us = duration_ns / 1000;
    __sync_fetch_and_add(&stats->sum_sq_duration_us, duration_us * duration_us);
  }

  if (duration_ns > 0) {
    u32 bucket = log2_u64(duration_ns);
    if (bucket >= HISTO_BUCKETS) {
        bucket = HISTO_BUCKETS - 1;
    }
    u32 histo_key = func_enum_key * HISTO_BUCKETS + bucket; 
    u64 *count = bpf_map_lookup_elem(&latency_histogram, &histo_key);
    if (count) {
        __sync_fetch_and_add(count, 1);
    }   
  }
        
  return 0;
}

SEC("kprobe/iommu_map")
int BPF_KPROBE(kprobe_iommu_map, struct iommu_domain *domain, unsigned long iova,
               phys_addr_t paddr, size_t size, int prot, gfp_t gfp)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/iommu_map")
int BPF_KRETPROBE(kretprobe_iommu_map, int ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/__iommu_map")
int BPF_KPROBE(kprobe___iommu_map, struct iommu_domain *domain, unsigned long iova,
               phys_addr_t paddr, size_t size, int prot, gfp_t gfp)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/__iommu_map")
int BPF_KRETPROBE(kretprobe___iommu_map, int ret_val)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/intel_iommu_iotlb_sync_map")
int BPF_KPROBE(kprobe_intel_iommu_iotlb_sync_map, struct iommu_domain *domain,
               unsigned long iova, size_t size)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/intel_iommu_iotlb_sync_map")
int BPF_KRETPROBE(kretprobe_intel_iommu_iotlb_sync_map, int ret_val)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/iommu_unmap")
int BPF_KPROBE(kprobe_iommu_unmap, struct iommu_domain *domain,
               unsigned long iova, size_t size)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/iommu_unmap")
int BPF_KRETPROBE(kretprobe_iommu_unmap, size_t ret_val)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/__iommu_unmap")
int BPF_KPROBE(kprobe___iommu_unmap, struct iommu_domain *domain,
               unsigned long iova, size_t size,
               struct iommu_iotlb_gather *iotlb_gather)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/__iommu_unmap")
int BPF_KRETPROBE(kretprobe___iommu_unmap, size_t ret_val)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/intel_iommu_tlb_sync")
int BPF_KPROBE(kprobe_intel_iommu_tlb_sync, struct iommu_domain *domain,
               struct iommu_iotlb_gather *gather)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/intel_iommu_tlb_sync")
int BPF_KRETPROBE(kretprobe_intel_iommu_tlb_sync)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/page_pool_alloc_netmem")
int BPF_KPROBE(kprobe_page_pool_alloc_netmem, struct page_pool *pool, gfp_t gfp)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/page_pool_alloc_netmem")
int BPF_KRETPROBE(kretprobe_page_pool_alloc_netmem, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/__page_pool_alloc_pages_slow")
int BPF_KPROBE(kprobe___page_pool_alloc_pages_slow, struct page_pool *pool, gfp_t gfp)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/__page_pool_alloc_pages_slow")
int BPF_KRETPROBE(kretprobe___page_pool_alloc_pages_slow, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}


SEC("kprobe/qi_submit_sync")
int BPF_KRETPROBE(kprobe_qi_submit_sync, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/qi_submit_sync")
int BPF_KRETPROBE(kretprobe_qi_submit_sync, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/qi_batch_flush_descs")
int BPF_KPROBE(kprobe_qi_batch_flush_descs, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/qi_batch_flush_descs")
int BPF_KRETPROBE(kretprobe_qi_batch_flush_descs, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/cache_tag_flush_range")
int BPF_KPROBE(kprobe_cache_tag_flush_range, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/cache_tag_flush_range")
int BPF_KRETPROBE(kretprobe_cache_tag_flush_range, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/cache_tag_flush_range_call")
int BPF_KPROBE(kprobe_cache_tag_flush_range_call, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/cache_tag_flush_range_call")
int BPF_KRETPROBE(kretprobe_cache_tag_flush_range_call, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/cache_tag_flush_range_np")
int BPF_KPROBE(kprobe_cache_tag_flush_range_np, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/cache_tag_flush_range_np")
int BPF_KRETPROBE(kretprobe_cache_tag_flush_range_np, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/iommu_flush_write_buffer")
int BPF_KPROBE(kprobe_iommu_flush_write_buffer, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/iommu_flush_write_buffer")
int BPF_KRETPROBE(kretprobe_iommu_flush_write_buffer, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/page_pool_dma_map")
int BPF_KPROBE(kprobe_page_pool_dma_map, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/page_pool_dma_map")
int BPF_KRETPROBE(kretprobe_page_pool_dma_map, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/page_pool_return_page")
int BPF_KPROBE(kprobe_page_pool_return_page, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/page_pool_return_page")
int BPF_KRETPROBE(kretprobe_page_pool_return_page, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/page_pool_put_unrefed_netmem")
int BPF_KPROBE(kprobe_page_pool_put_unrefed_netmem, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/page_pool_put_unrefed_netmem")
int BPF_KRETPROBE(kretprobe_page_pool_put_unrefed_netmem, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/page_pool_put_unrefed_page")
int BPF_KPROBE(kprobe_page_pool_put_unrefed_page, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/page_pool_put_unrefed_page")
int BPF_KRETPROBE(kretprobe_page_pool_put_unrefed_page, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}


SEC("kprobe/trace_mlx5e_tx_dma_unmap_ktls_hook")
int BPF_KPROBE(kprobe_trace_mlx5e_tx_dma_unmap_ktls_hook, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_mlx5e_tx_dma_unmap_ktls_hook")
int BPF_KRETPROBE(kretprobe_trace_mlx5e_tx_dma_unmap_ktls_hook, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_mlx5e_dma_push_build_single_hook")
int BPF_KPROBE(kprobe_trace_mlx5e_dma_push_build_single_hook, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_mlx5e_dma_push_build_single_hook")
int BPF_KRETPROBE(kretprobe_trace_mlx5e_dma_push_build_single_hook, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_mlx5e_dma_push_xmit_single_hook")
int BPF_KPROBE(kprobe_trace_mlx5e_dma_push_xmit_single_hook, void *ret)
{
  return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_mlx5e_dma_push_xmit_single_hook")
int BPF_KRETPROBE(kretprobe_trace_mlx5e_dma_push_xmit_single_hook, void *ret)
{
  return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_mlx5e_dma_push_page_hook")
int BPF_KPROBE(kprobe_trace_mlx5e_dma_push_page_hook, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_mlx5e_dma_push_page_hook")
int BPF_KRETPROBE(kretprobe_trace_mlx5e_dma_push_page_hook, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_mlx5e_tx_dma_unmap_hook")
int BPF_KPROBE(kprobe_trace_mlx5e_tx_dma_unmap_hook, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_mlx5e_tx_dma_unmap_hook")
int BPF_KRETPROBE(kretprobe_trace_mlx5e_tx_dma_unmap_hook, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_qi_submit_sync_cs")
int BPF_KPROBE(kprobe_trace_qi_submit_sync_cs, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_qi_submit_sync_cs")
int BPF_KRETPROBE(kretprobe_trace_qi_submit_sync_cs, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_qi_submit_sync_lock_wrapper")
int BPF_KPROBE(kprobe_trace_qi_submit_sync_lock_wrapper, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_qi_submit_sync_lock_wrapper")
int BPF_KRETPROBE(kretprobe_trace_qi_submit_sync_lock_wrapper, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_iommu_flush_write_buffer_cs")
int BPF_KPROBE(kprobe_trace_iommu_flush_write_buffer_cs, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_iommu_flush_write_buffer_cs")
int BPF_KRETPROBE(kretprobe_trace_iommu_flush_write_buffer_cs, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/trace_iommu_flush_write_buffer_lock_wrapper")
int BPF_KPROBE(kprobe_trace_iommu_flush_write_buffer_lock_wrapper, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/trace_iommu_flush_write_buffer_lock_wrapper")
int BPF_KRETPROBE(kretprobe_trace_iommu_flush_write_buffer_lock_wrapper, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/writel_wrapper")
int BPF_KPROBE(kprobe_writel_wrapper, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/writel_wrapper")
int BPF_KRETPROBE(kretprobe_writel_wrapper, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/after_writel_while_wrapper")
int BPF_KPROBE(kprobe_after_writel_while_wrapper, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/after_writel_while_wrapper")
int BPF_KRETPROBE(kretprobe_after_writel_while_wrapper, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/iommu_dma_free_iova")
int BPF_KPROBE(kprobe_iommu_dma_free_iova, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/iommu_dma_free_iova")
int BPF_KRETPROBE(kretprobe_iommu_dma_free_iova, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/iommu_dma_free_iova_call")
int BPF_KPROBE(kprobe_iommu_dma_free_iova_call, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/iommu_dma_free_iova_call")
int BPF_KRETPROBE(kretprobe_iommu_dma_free_iova_call, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/__iommu_dma_unmap_call")
int BPF_KPROBE(kprobe___iommu_dma_unmap_call, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/__iommu_dma_unmap_call")
int BPF_KRETPROBE(kretprobe___iommu_dma_unmap_call, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/__iommu_dma_unmap")
int BPF_KPROBE(kprobe___iommu_dma_unmap, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/__iommu_dma_unmap")
int BPF_KRETPROBE(kretprobe___iommu_dma_unmap, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/count_mlx5e_alloc_rx_mpwqe_perpage_hook")
int BPF_KPROBE(kprobe_count_mlx5e_alloc_rx_mpwqe_perpage_hook, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/count_mlx5e_alloc_rx_mpwqe_perpage_hook")
int BPF_KRETPROBE(kretprobe_count_mlx5e_alloc_rx_mpwqe_perpage_hook, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/count_page_pool_release_page_dma_hook")
int BPF_KPROBE(kprobe_count_page_pool_release_page_dma_hook, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/count_page_pool_release_page_dma_hook")
int BPF_KRETPROBE(kretprobe_count_page_pool_release_page_dma_hook, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/count_page_pool_recycle_in_cache_hook")
int BPF_KPROBE(kprobe_count_page_pool_recycle_in_cache_hook, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/count_page_pool_recycle_in_cache_hook")
int BPF_KRETPROBE(kretprobe_count_page_pool_recycle_in_cache_hook, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/sys_flush_handler")
int BPF_KPROBE(kprobe_sys_flush_handler, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/sys_flush_handler")
int BPF_KRETPROBE(kretprobe_sys_flush_handler, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/__sys_flush_handler")
int BPF_KPROBE(kprobe___sys_flush_handler, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/__sys_flush_handler")
int BPF_KRETPROBE(kretprobe___sys_flush_handler, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/dma_map_sg_attrs")
int BPF_KPROBE(kprobe_dma_map_sg_attrs, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/dma_map_sg_attrs")
int BPF_KRETPROBE(kretprobe_dma_map_sg_attrs, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/sk_stream_wait_memory")
int BPF_KPROBE(kprobe_sk_stream_wait_memory, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/sk_stream_wait_memory")
int BPF_KRETPROBE(kretprobe_sk_stream_wait_memory, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/iova_free_from_qi_batch")
int BPF_KPROBE(kprobe_iova_free_from_qi_batch, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/iova_free_from_qi_batch")
int BPF_KRETPROBE(kretprobe_iova_free_from_qi_batch, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/unmap_callback_consume")
int BPF_KPROBE(kprobe_unmap_callback_consume, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/unmap_callback_consume")
int BPF_KRETPROBE(kretprobe_unmap_callback_consume, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}

SEC("kprobe/cache_tag_flush_iotlb")
int BPF_KPROBE(kprobe_cache_tag_flush_iotlb, void *ret)
{
    return _bpf_utils_trace_func_entry(ctx);
}

SEC("kretprobe/cache_tag_flush_iotlb")
int BPF_KRETPROBE(kretprobe_cache_tag_flush_iotlb, void *ret)
{
    return _bpf_utils_trace_func_exit(ctx, GUEST, false);
}
