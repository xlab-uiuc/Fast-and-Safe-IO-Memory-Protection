#ifndef __TRACING_UTILS_H__
#define __TRACING_UTILS_H__

#ifndef BPF_CORE
typedef unsigned long long u64;
typedef long long s64;
typedef unsigned int u32;
typedef int s32;
#endif // BPF_CORE

#ifndef BPF_MAX_STACK_DEPTH
#define BPF_MAX_STACK_DEPTH 127
#endif

#define HISTO_BUCKETS 21

enum Domain
{
  GUEST = 0,
  HOST = 1,
  QEMU = 2,
};

enum FunctionName
{
    // --- Section for Latency Tracing ---
    TRACE_FUNC_START = 0,
    IOMMU_MAP = TRACE_FUNC_START,
    IOMMU_MAP_INTERNAL,
    IOMMU_IOTLB_SYNC_MAP, // intel_iommu_iotlb_sync_map
    IOMMU_UNMAP,
    CACHE_TAG_FLUSH_RANGE_NP,
    IOMMU_FLUSH_WRITE_BUFFER,
    IOMMU_UNMAP_INTERNAL,
    IOMMU_TLB_SYNC, // intel_iommu_tlb_sync
    CACHE_TAG_FLUSH_RANGE,
    PAGE_POOL_ALLOC,
    PAGE_POOL_SLOW,
    QI_SUBMIT_SYNC,
    QI_BATCH_FLUSH_DESCS,
    TRACE_MLX5E_TX_DMA_UNMAP_KTLS_HOOK,
    TRACE_MLX5E_DMA_PUSH_BUILD_SINGLE_HOOK,
    TRACE_MLX5E_DMA_PUSH_XMIT_SINGLE_HOOK,
    TRACE_MLX5E_DMA_PUSH_PAGE_HOOK,
    TRACE_MLX5E_TX_DMA_UNMAP_HOOK,
    TRACE_QI_SUBMIT_SYNC_CS,
    TRACE_QI_SUBMIT_SYNC_LOCK_WRAPPER,
    TRACE_IOMMU_FLUSH_WRITE_BUFFER_CS,
    TRACE_IOMMU_FLUSH_WRITE_BUFFER_LOCK_WRAPPER,
    PAGE_POOL_DMA_MAP,
    PAGE_POOL_RETURN_PAGE,
    PAGE_POOL_PUT_NETMEM,
    PAGE_POOL_PUT_PAGE,
    QEMU_VTD_FETCH_INV_DESC,
    TRACE_FUNCS_END, // Marks the end of trace functions

    // --- Section for Simple Frequency Counting ---
    COUNT_FUNC_START = TRACE_FUNCS_END,
    COUNT_PAGE_POOL_RELEASE = COUNT_FUNC_START,
    COUNT_PAGE_POOL_RECYCLE,
    COUNT_MLX5E_RX_MPWQE_PER_PAGE,
    COUNT_FUNCS_END,

    FUNCTION_NAME_MAX = COUNT_FUNCS_END,
};

struct entry_key_t
{
  u64 id;
  u64 cookie;
};

struct entry_val_t
{
  u64 ts;
};

struct ioctl_trace_val_t
{
  u64 ts;           // Timestamp of the entry
  unsigned int cmd; // The ioctl command being traced
};

struct data_t
{
  enum Domain domain;
  enum FunctionName func_name;
  u32 pid;
  u32 tid;
  u32 cpu_id;
  u64 timestamp_ns;
  u64 duration_ns;
  s64 kern_stack_id;
  s64 user_stack_id;
};

struct latency_stats_t
{
  u64 count;
  u64 total_duration_ns;  // Sum of all durations
  u64 sum_sq_duration_us; // Sum of (duration * duration)
};

#endif // __TRACING_UTILS_H__
