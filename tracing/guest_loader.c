#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <argp.h>
#include <limits.h>
#include <math.h>

#include <bpf/libbpf.h>
#include <bpf/bpf.h>

#include "guest_tracer.skel.h"
#include "tracing_utils.h"

#define PERF_BUFFER_PAGES 64
#define MAX_PROBES 50
#define MAX_STACK_DEPTH 127

static volatile bool exiting = false;
static FILE *output_agg_data_file = NULL;

// --- Command Line Argument Parsing ---
static struct arguments
{
  int duration_sec;
  bool verbose;
  char *agg_data_filepath;
} args = {
    .duration_sec = 30,
    .verbose = false,
    .agg_data_filepath = "guest_aggregate.csv",
};

static char doc[] = "eBPF loader for kernel tracing.";
static char args_doc[] = "";
static struct argp_option opts[] = {
    {"duration", 'd', "SECONDS", 0, "Duration to run the tracer (0 for infinite, default: 30)"},
    {"verbose", 'v', NULL, 0, "Enable libbpf verbose logging"},
    {"agg-data-file", 'o', "FILE", 0, "Output structured aggregate data to CSV FILE (e.g., agg_data.csv)."},
    {NULL}};

static error_t parse_arg(int key, char *arg, struct argp_state *state)
{
  struct arguments *arguments = state->input;
  switch (key)
  {
  case 'd':
    arguments->duration_sec = atoi(arg);
    break;
  case 'v':
    arguments->verbose = true;
    break;
  case 'o':
    arguments->agg_data_filepath = arg;
    break;
  case ARGP_KEY_ARG:
    return ARGP_ERR_UNKNOWN;
  default:
    return ARGP_ERR_UNKNOWN;
  }
  return 0;
}

static struct argp argp_parser = {
    .options = opts,
    .parser = parse_arg,
    .args_doc = args_doc,
    .doc = doc,
};

static void sig_handler(int sig)
{
  (void)sig;
  exiting = true;
}

// Probe Definitions (ensure FunctionName enum values match cookies)
typedef enum
{
  PROBE_TYPE_KPROBE,
  PROBE_TYPE_KRETPROBE,
} probe_type_t;

typedef struct
{
  const char *bpf_prog_name;
  const char *target_name;
  probe_type_t type;
  enum FunctionName cookie;
} probe_def_t;

probe_def_t probes_to_attach[] = {
    {"kprobe_iommu_map", "iommu_map", PROBE_TYPE_KPROBE, IOMMU_MAP},
    {"kretprobe_iommu_map", "iommu_map", PROBE_TYPE_KRETPROBE, IOMMU_MAP},
    {"kprobe___iommu_map", "__iommu_map", PROBE_TYPE_KPROBE, IOMMU_MAP_INTERNAL},
    {"kretprobe___iommu_map", "__iommu_map", PROBE_TYPE_KRETPROBE, IOMMU_MAP_INTERNAL},
    {"kprobe_intel_iommu_iotlb_sync_map", "intel_iommu_iotlb_sync_map", PROBE_TYPE_KPROBE, IOMMU_IOTLB_SYNC_MAP},
    {"kretprobe_intel_iommu_iotlb_sync_map", "intel_iommu_iotlb_sync_map", PROBE_TYPE_KRETPROBE, IOMMU_IOTLB_SYNC_MAP},
    //cache_tag_flush_range_np
    {"kprobe_cache_tag_flush_range_np", "cache_tag_flush_range_np", PROBE_TYPE_KPROBE, CACHE_TAG_FLUSH_RANGE_NP},
    {"kretprobe_cache_tag_flush_range_np", "cache_tag_flush_range_np", PROBE_TYPE_KRETPROBE, CACHE_TAG_FLUSH_RANGE_NP},
    // iommu_flush_write_buffer
    {"kprobe_iommu_flush_write_buffer", "iommu_flush_write_buffer", PROBE_TYPE_KPROBE, IOMMU_FLUSH_WRITE_BUFFER},
    {"kretprobe_iommu_flush_write_buffer", "iommu_flush_write_buffer", PROBE_TYPE_KRETPROBE, IOMMU_FLUSH_WRITE_BUFFER},
    {"kprobe_iommu_unmap", "iommu_unmap", PROBE_TYPE_KPROBE, IOMMU_UNMAP},
    {"kretprobe_iommu_unmap", "iommu_unmap", PROBE_TYPE_KRETPROBE, IOMMU_UNMAP},
    {"kprobe___iommu_unmap", "__iommu_unmap", PROBE_TYPE_KPROBE, IOMMU_UNMAP_INTERNAL},
    {"kretprobe___iommu_unmap", "__iommu_unmap", PROBE_TYPE_KRETPROBE, IOMMU_UNMAP_INTERNAL},
    {"kprobe_intel_iommu_tlb_sync", "intel_iommu_tlb_sync", PROBE_TYPE_KPROBE, IOMMU_TLB_SYNC},
    {"kretprobe_intel_iommu_tlb_sync", "intel_iommu_tlb_sync", PROBE_TYPE_KRETPROBE, IOMMU_TLB_SYNC},
    // cache_tag_flush_range
    {"kprobe_cache_tag_flush_range", "cache_tag_flush_range", PROBE_TYPE_KPROBE, CACHE_TAG_FLUSH_RANGE},
    {"kretprobe_cache_tag_flush_range", "cache_tag_flush_range", PROBE_TYPE_KRETPROBE, CACHE_TAG_FLUSH_RANGE},
    {"kprobe_page_pool_alloc_netmem", "page_pool_alloc_netmem", PROBE_TYPE_KPROBE, PAGE_POOL_ALLOC},
    {"kretprobe_page_pool_alloc_netmem", "page_pool_alloc_netmem", PROBE_TYPE_KRETPROBE, PAGE_POOL_ALLOC},
    {"kprobe___page_pool_alloc_pages_slow", "__page_pool_alloc_pages_slow", PROBE_TYPE_KPROBE, PAGE_POOL_SLOW},
    {"kretprobe___page_pool_alloc_pages_slow", "__page_pool_alloc_pages_slow", PROBE_TYPE_KRETPROBE, PAGE_POOL_SLOW},
    {"kprobe_qi_submit_sync", "qi_submit_sync", PROBE_TYPE_KPROBE, QI_SUBMIT_SYNC },
    {"kretprobe_qi_submit_sync", "qi_submit_sync", PROBE_TYPE_KRETPROBE, QI_SUBMIT_SYNC},
    // qi_batch_flush_descs
    {"kprobe_qi_batch_flush_descs", "qi_batch_flush_descs", PROBE_TYPE_KPROBE, QI_BATCH_FLUSH_DESCS},
    {"kretprobe_qi_batch_flush_descs", "qi_batch_flush_descs", PROBE_TYPE_KRETPROBE, QI_BATCH_FLUSH_DESCS},
    {"kprobe_qi_submit_sync", "qi_submit_sync", PROBE_TYPE_KPROBE, QI_SUBMIT_SYNC },
    {"kretprobe_qi_submit_sync", "qi_submit_sync", PROBE_TYPE_KRETPROBE, QI_SUBMIT_SYNC},
};
const int num_probes_to_attach = sizeof(probes_to_attach) / sizeof(probes_to_attach[0]);
struct bpf_link *attached_links[MAX_PROBES];

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args_list)
{
  if (level == LIBBPF_DEBUG && !args.verbose)
    return 0;
  return vfprintf(stderr, format, args_list);
}

const char *func_name_to_string(enum FunctionName fn)
{
  switch (fn)
  {
  case IOMMU_MAP:
    return "iommu_map";
  case IOMMU_MAP_INTERNAL:
    return "__iommu_map";
  case IOMMU_IOTLB_SYNC_MAP:
    return "intel_iommu_iotlb_sync_map";
  case CACHE_TAG_FLUSH_RANGE_NP:
    return "cache_tag_flush_range_np";
  case IOMMU_FLUSH_WRITE_BUFFER:
    return "iommu_flush_write_buffer";
  case IOMMU_UNMAP:
    return "iommu_unmap";
  case IOMMU_UNMAP_INTERNAL:
    return "__iommu_unmap";
  case IOMMU_TLB_SYNC:
    return "intel_iommu_tlb_sync";
  case CACHE_TAG_FLUSH_RANGE:
    return "cache_tag_flush_range";
  case PAGE_POOL_ALLOC:
    return "page_pool_alloc_netmem";
  case PAGE_POOL_SLOW:
    return "page_pool_alloc_pages_slow";
  case QI_BATCH_FLUSH_DESCS:
    return "qi_batch_flush_descs";
  case QI_SUBMIT_SYNC:
    return "qi_submit_sync";
  default:
    return "UnknownFunction";
  }
}

static void dump_aggregate_to_file(FILE *fp, struct guest_tracer_bpf *skel)
{
  if (!fp) 
    return;

  int num_cpus = libbpf_num_possible_cpus();
  if (num_cpus <= 0) {
    fprintf(stderr, "ERROR: Could not get number of possible CPUs\n");
    return;
  }

  int stats_fd = bpf_map__fd(skel->maps.func_latency_stats);
  int counts_fd = bpf_map__fd(skel->maps.func_call_counts);
  int histo_fd = bpf_map__fd(skel->maps.latency_histogram);

  unsigned long long agg_stats_counts[FUNCTION_NAME_MAX] = {0};
  
  unsigned long long agg_stats_total_durations_ns[TRACE_FUNCS_END] = {0};
  double agg_stats_mean_ns[TRACE_FUNCS_END] = {0.0};  
  double agg_stats_variance_us[TRACE_FUNCS_END] = {0.0};

  fprintf(fp, "# Per-Function Per-CPU Latency Statistics\n");
  fprintf(fp, "function,cpu,count,total_duration_ns,mean_ns,variance_us\n");

  for (int fn = 0; fn < TRACE_FUNCS_END; fn++) {
    const char *fn_name = func_name_to_string((enum FunctionName)fn);
    size_t per_cpu_sz = sizeof(struct latency_stats_t);
    size_t buf_sz = per_cpu_sz * num_cpus;
    struct latency_stats_t *percpu_stats = malloc(buf_sz);
    if (!percpu_stats || bpf_map_lookup_elem(stats_fd, &fn, percpu_stats) != 0) {
      free(percpu_stats);
      continue;
    }

    __u64 total_count = 0;
    __u64 total_duration_ns = 0;
    __u64 total_sum_sq_us = 0;
      
    for (int cpu = 0; cpu < num_cpus; cpu++) {
      struct latency_stats_t *s = &percpu_stats[cpu];
      if (s->count == 0) continue;
        
      fprintf(fp, "%s,%d,%llu,%llu,%.2f,%.2f\n",
              fn_name,
              cpu,
              (unsigned long long)s->count,
              (unsigned long long)s->total_duration_ns,
              (double)s->total_duration_ns / (double)s->count, 
              0.0);
        
      total_count += s->count;
      total_duration_ns += s->total_duration_ns;
      total_sum_sq_us += s->sum_sq_duration_us;
    }

    free(percpu_stats);

    if (total_count == 0) 
      continue;

    double mean_ns = (double)total_duration_ns / (double)total_count;
    double mean_us = mean_ns / 1000.0;

    // variance in µs units = E[x²] – (E[x])², where x is duration in µs
    double variance_us = ((double)total_sum_sq_us / (double)total_count) - (mean_us * mean_us);
    agg_stats_counts[fn] = total_count;
    agg_stats_total_durations_ns[fn] = total_duration_ns;
    agg_stats_mean_ns[fn] = mean_ns;
    agg_stats_variance_us[fn] = variance_us;
  }

  fprintf(fp, "# Per-Function Latency Statistics\n");
  fprintf(fp, "function,type,count,total_duration_ns,mean_ns,variance_us\n");
  
  for (int fn = 0; fn < TRACE_FUNCS_END; fn++) {
    if (agg_stats_counts[fn] == 0)
      continue;
    
    const char *fn_name = func_name_to_string((enum FunctionName)fn);
    fprintf(fp, "%s,%d,%llu,%llu,%.2f,%.2f\n",
            fn_name,
            -1, 
            (unsigned long long)agg_stats_counts[fn],
            (unsigned long long)agg_stats_total_durations_ns[fn],
            agg_stats_mean_ns[fn],
            agg_stats_variance_us[fn]);
  }

  fprintf(fp, "# Per-Function Per-CPU Counts\n");
  fprintf(fp, "function,cpu,count\n");

  for (int fn = TRACE_FUNCS_END; fn < FUNCTION_NAME_MAX; fn++) {
    const char *fn_name = func_name_to_string((enum FunctionName)fn);
    size_t counts_sz = sizeof(__u64) * num_cpus;
    __u64 *percpu_counts = malloc(counts_sz);
    if (!percpu_counts || bpf_map_lookup_elem(counts_fd, &fn, percpu_counts) != 0) {
      free(percpu_counts);
      continue;
    }

    __u64 total_count = 0;
    for (int cpu = 0; cpu < num_cpus; cpu++) {
      fprintf(fp, "%s,%d,%llu\n",
            fn_name,
            cpu,
            (unsigned long long)percpu_counts[cpu]);
        
      total_count += percpu_counts[cpu];
    }
    free(percpu_counts);

    if (total_count == 0) continue;
    agg_stats_counts[fn] = total_count;
  }

  fprintf(fp, "# Per-Function Counts\n");
  fprintf(fp, "function,type,count\n");
  for (int fn = TRACE_FUNCS_END; fn < FUNCTION_NAME_MAX; fn++) {
    if (agg_stats_counts[fn] == 0)
      continue;

    const char *fn_name = func_name_to_string((enum FunctionName)fn);
    fprintf(fp, "%s,%d,%llu\n",
          fn_name,
          -1, 
          (unsigned long long)agg_stats_counts[fn]);
  }
      
  // --- Print Per-Function Histograms ---
  fprintf(fp, "\n# Per-Function Latency Histograms\n");
  fprintf(fp, "function,bucket,latency_range_ns,count\n");

  for (int fn = 0; fn < TRACE_FUNCS_END; fn++) {
    const char *fn_name = func_name_to_string((enum FunctionName)fn);
    bool has_output = false;

    for (int bucket = 0; bucket < HISTO_BUCKETS; bucket++) {
      u32 histo_key = fn * HISTO_BUCKETS + bucket;
      size_t counts_sz = sizeof(__u64) * num_cpus;
      __u64 *percpu_counts = malloc(counts_sz);
      if (!percpu_counts || bpf_map_lookup_elem(histo_fd, &histo_key, percpu_counts) != 0) {
        free(percpu_counts);
        continue;
      }

      __u64 total_count = 0;
      for (int cpu = 0; cpu < num_cpus; cpu++) {
        total_count += percpu_counts[cpu];
      }
      free(percpu_counts);

      if (total_count > 0) {
        has_output = true;
        unsigned long long lower = (unsigned long long)pow(2, bucket);
        unsigned long long upper = (unsigned long long)pow(2, bucket + 1) - 1;
        fprintf(fp, "%s,%d,\"%llu - %llu ns\",%llu\n", fn_name, bucket, lower, upper, total_count);
      }
    }
    if(has_output) fprintf(fp, "\n"); // Add a blank line between function histograms
  }
}

int main(int argc, char **argv)
{
  struct guest_tracer_bpf *skel = NULL;
  int err = 0;
  struct timespec start_ts, now_ts;
  int attached_count = 0;

  err = argp_parse(&argp_parser, argc, argv, 0, NULL, &args);
  if (err)
    return err;

  if (args.agg_data_filepath)
  {
    output_agg_data_file = fopen(args.agg_data_filepath, "w"); // Create/overwrite
    if (!output_agg_data_file)
    {
      perror("Failed to open output file for aggregate data");
      return EXIT_FAILURE;
    }
    printf("Outputting structured aggregate data to: %s\n", args.agg_data_filepath);
  }

  libbpf_set_strict_mode(LIBBPF_STRICT_ALL);
  libbpf_set_print(libbpf_print_fn);

  skel = guest_tracer_bpf__open_and_load();
  if (!skel)
  {
    fprintf(stderr, "Failed to open BPF skeleton\n");
    err = 1;
    goto cleanup_file;
  }

  printf("Attaching probes... time=%ld\n", time(NULL));
  for (int i = 0; i < num_probes_to_attach; i++)
  {
    probe_def_t *p_def = &probes_to_attach[i];
    struct bpf_program *prog = bpf_object__find_program_by_name(skel->obj, p_def->bpf_prog_name);
    if (!prog)
    {
      fprintf(stderr, "Failed to find BPF program '%s' in skeleton\n", p_def->bpf_prog_name);
      err = -ENOENT;
      goto cleanup_file;
    }

    struct bpf_link *link = NULL;
    if (p_def->type == PROBE_TYPE_KPROBE)
    {
      LIBBPF_OPTS(bpf_kprobe_opts, k_opts, .bpf_cookie = p_def->cookie);
      link = bpf_program__attach_kprobe_opts(prog, p_def->target_name, &k_opts);
    }
    else if (p_def->type == PROBE_TYPE_KRETPROBE)
    {
      LIBBPF_OPTS(bpf_kprobe_opts, kr_opts, .bpf_cookie = p_def->cookie, .retprobe = true);
      link = bpf_program__attach_kprobe_opts(prog, p_def->target_name, &kr_opts);
    }

    if (!link || libbpf_get_error(link))
    {
      err = libbpf_get_error(link);
      fprintf(stderr, "Failed to attach %s '%s' to '%s': %s\n",
              p_def->type == PROBE_TYPE_KPROBE ? "kprobe" : "kretprobe",
              p_def->bpf_prog_name, p_def->target_name, strerror(-err));
      goto cleanup_file;
    }
    attached_links[attached_count++] = link;
  }
  printf("All %d probes attached successfully. time=%ld\n", attached_count, time(NULL));

  signal(SIGINT, sig_handler);
  signal(SIGTERM, sig_handler);

  printf("Tracer started. Hit Ctrl-C to end or run for %d seconds.\n", args.duration_sec);

  clock_gettime(CLOCK_MONOTONIC, &start_ts);

  while (!exiting)
  {
    if (args.duration_sec > 0)
    {
      clock_gettime(CLOCK_MONOTONIC, &now_ts);
      if (now_ts.tv_sec - start_ts.tv_sec >= args.duration_sec)
      {
        exiting = true;
        break;
      }
    }
    usleep(500000);
  }

  // Final histogram print and stack map dump
  if (skel && output_agg_data_file)
    dump_aggregate_to_file(output_agg_data_file, skel);

cleanup_file:
  if (output_agg_data_file)
  {
    printf("Closing aggregate data file: %s time=%ld\n", args.agg_data_filepath, time(NULL));
    if (fclose(output_agg_data_file) != 0)
      perror("Failed to close aggregate data file");
    output_agg_data_file = NULL;
  }
  for (int i = 0; i < attached_count; i++)
  {
    if (attached_links[i])
    {
      bpf_link__destroy(attached_links[i]);
      attached_links[i] = NULL;
    }
  }
  if (skel)
  {
    guest_tracer_bpf__destroy(skel);
    skel = NULL;
  }
  printf("Guest BPF Cleanup complete. Exiting with code %d.\n", err ? 1 : 0);
  return err ? 1 : 0;
}
