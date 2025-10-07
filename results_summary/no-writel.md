

## Skip writel inside qi_submit_sync
```
------- 2025-10-06-19-38-52-6.12.9-iommufd-no-writel-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores Run Metrics -------
Throughput: 221.323
CPU Util: 99.9435
Drop rate: 2.16e-06
Acks per page: 0.016818608357920324
Per page stats:
        IOTLB Miss: 1.193588035875169
        IOTLB First Lookup: 10.154951503097283
        IOTLB All Lookups: 18.511458759769134
        IOTLB Inv: 0.10790433717236798
        IOMMU Mem Access: 2.46306754547878
        PWT Occupancy: 1327972808.688
Reading eBPF stats from ../utils/reports/2025-10-06-19-38-52-6.12.9-iommufd-no-writel-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns      mean_ns   variance_us  count_per_page
0                      iommu_map    -1   1047815        23282950277     22220.48  6.153900e+02        0.007757
1                    __iommu_map    -1   1047503         1331851370      1271.45 -5.200000e-01        0.007754
2     intel_iommu_iotlb_sync_map    -1   1047164        19863291284     18968.65  6.142500e+02        0.007752
3       cache_tag_flush_range_np    -1   1046841        18529973119     17700.85  6.150900e+02        0.007750
4       iommu_flush_write_buffer    -1   1046515          750177138       716.83 -1.000000e-01        0.007747
5                  __iommu_unmap    -1   1045850         1659236044      1586.50 -6.100000e-01        0.007742
6           intel_iommu_tlb_sync    -1   1045530        29404222953     28123.75  3.974000e+02        0.007740
7          cache_tag_flush_range    -1   1045243        27779604559     26577.17  3.964100e+02        0.007738
8                 qi_submit_sync    -1   1043958        12048701206     11541.37  8.735000e+01        0.007728
9           qi_batch_flush_descs    -1   2088451        14317708334      6855.66  8.300000e+01        0.015460
10       trace_qi_submit_sync_cs    -1   1043377        10693274521     10248.72  8.539000e+01        0.007724
11  page_pool_put_unrefed_netmem    -1  47632317        42919767274       901.06  2.200000e-01        0.352610
12    page_pool_put_unrefed_page    -1     59655      2273501167146  38110823.35  2.165818e+13        0.000442
```

```
------- 2025-10-06-20-29-06-6.12.9-iommufd-no-writel-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores Run Metrics -------
Throughput: 344.445
CPU Util: 88.65359375
Drop rate: 0.0006922006
Acks per page: 0.04947615057498294
Per page stats:
        IOTLB Miss: 1.1823682853053463
        IOTLB First Lookup: 10.051158940975725
        IOTLB All Lookups: 18.71930524478509
        IOTLB Inv: 0.0
        IOMMU Mem Access: 2.3886559346902527
        PWT Occupancy: 2404329229.812
Reading eBPF stats from ../utils/reports/2025-10-06-20-29-06-6.12.9-iommufd-no-writel-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns      mean_ns   variance_us  count_per_page
0                      iommu_map    -1   1812756        33672264078     18575.18  7.445000e+01        0.008623
1                    __iommu_map    -1   1810810         3166224794      1748.51 -3.300000e-01        0.008613
2     intel_iommu_iotlb_sync_map    -1   1809203        25750148415     14232.87  6.754000e+01        0.008606
3       cache_tag_flush_range_np    -1   1807744        22765040935     12593.07  6.628000e+01        0.008599
4       iommu_flush_write_buffer    -1   1806428         2277398114      1260.72  5.800000e-01        0.008593
5                  __iommu_unmap    -1   1804470         3720187399      2061.65 -8.000000e-02        0.008583
6           intel_iommu_tlb_sync    -1   1803452        29789340349     16517.96  7.166000e+01        0.008578
7          cache_tag_flush_range    -1   1802531        26262353258     14569.71  7.034000e+01        0.008574
8                 qi_submit_sync    -1   1798525         4777184118      2656.17  2.800000e-01        0.008555
9           qi_batch_flush_descs    -1   3598571        10213020018      2838.08  3.900000e+00        0.017117
10       trace_qi_submit_sync_cs    -1   1797013         1666616643       927.44  1.000000e-01        0.008548
11  page_pool_put_unrefed_netmem    -1  75371077       103532980185      1373.64  4.700000e-01        0.358513
12    page_pool_put_unrefed_page    -1    286598      5549429177935  19363112.02  3.359202e+12        0.001363
```

```
------- 2025-10-06-20-33-59-6.12.9-iommufd-no-writel-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores Run Metrics -------
Throughput: 273.807
CPU Util: 88.6303
Drop rate: 0.0008421404
Acks per page: 0.027850167138166664
Per page stats:
        IOTLB Miss: 1.1876182486481939
        IOTLB First Lookup: 10.057482141626705
        IOTLB All Lookups: 16.625878772712163
        IOTLB Inv: 0.0
        IOMMU Mem Access: 2.371095155346649
        PWT Occupancy: 1754318361.312
Reading eBPF stats from ../utils/reports/2025-10-06-20-33-59-6.12.9-iommufd-no-writel-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns      mean_ns   variance_us  count_per_page
0                      iommu_map    -1   3132235     70782379754734  22598042.53  4.326659e+12    1.874260e-02
1                    __iommu_map    -1   3128350         6072035322      1940.97 -8.000000e-02    1.871935e-02
2     intel_iommu_iotlb_sync_map    -1   3125110     18683662375656   5978561.51  2.691555e+12    1.869996e-02
3       cache_tag_flush_range_np    -1   3122556     11432105531267   3661137.07  1.642538e+12    1.868468e-02
4       iommu_flush_write_buffer    -1   3119714         4732753253      1517.05  3.700000e-01    1.866767e-02
5                  __iommu_unmap    -1   3107225         6504158151      2093.24  3.100000e-01    1.859294e-02
6           intel_iommu_tlb_sync    -1   2933930       571113353457    194658.14  6.992730e+10    1.755598e-02
7          cache_tag_flush_range    -1   2830536       565955611454    199946.45  7.248161e+10    1.693730e-02
8     page_pool_alloc_pages_slow    -1        10           85974405   8597440.50  6.412534e+06    5.983777e-08
9                 qi_submit_sync    -1   2517698         8268650461      3284.21  2.150000e+00    1.506534e-02
10          qi_batch_flush_descs    -1   5226719        17182429639      3287.42  8.630000e+00    3.127552e-02
11       trace_qi_submit_sync_cs    -1   2425961         3092718584      1274.84  4.400000e-01    1.451641e-02
12             page_pool_dma_map    -1       576           83552389    145056.23  2.081800e+02    3.446655e-06
13  page_pool_put_unrefed_netmem    -1  94866517        97957354275      1032.58  3.000000e-01    5.676601e-01
14    page_pool_put_unrefed_page    -1     17649           31020915      1757.66  7.000000e-02    1.056077e-04
```


## Skip writel by completely skipping adding inv desc to the queue
```
------- 2025-10-06-19-20-34-6.12.9-iommufd-no-writel-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores Run Metrics -------
Throughput: 205.745
CPU Util: 18.4179375
Drop rate: 0.0002968918
Acks per page: 0.024417714370701595
Per page stats:
        IOTLB Miss: 1.109332706970201
        IOTLB First Lookup: 9.793780529278864
        IOTLB All Lookups: 18.30769636900046
        IOTLB Inv: 0.0
        IOMMU Mem Access: 2.0692728206013467
        PWT Occupancy: 1167869442.235
Reading eBPF stats from ../utils/reports/2025-10-06-19-20-34-6.12.9-iommufd-no-writel-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores-RUN-0/ebpf_guest_stats.csv
                        function  type    count  total_duration_ns      mean_ns   variance_us  count_per_page
0                      iommu_map    -1    51094      2535634400119  49626852.47  4.192656e+13    4.068746e-04
1                    __iommu_map    -1    51117           86530820      1692.80 -1.010000e+00    4.070577e-04
2     intel_iommu_iotlb_sync_map    -1    51105       845660382643  16547507.73  1.398393e+13    4.069622e-04
3       cache_tag_flush_range_np    -1    51106          204407715      3999.68 -3.690000e+00    4.069701e-04
4       iommu_flush_write_buffer    -1    51111           41164866       805.40 -5.200000e-01    4.070100e-04
5                  __iommu_unmap    -1    50215           66860701      1331.49 -1.200000e-01    3.998749e-04
6           intel_iommu_tlb_sync    -1    50214          198388710      3950.86 -4.300000e+00    3.998669e-04
7          cache_tag_flush_range    -1    50214          121889266      2427.40 -1.060000e+00    3.998669e-04
8     page_pool_alloc_pages_slow    -1       14           27952081   1996577.21  2.951799e+05    1.114856e-07
9           qi_batch_flush_descs    -1   101332           79839949       787.90 -5.300000e-01    8.069326e-04
10             page_pool_dma_map    -1      896           25555232     28521.46  2.094390e+03    7.135077e-06
11  page_pool_put_unrefed_netmem    -1  2526972         2140852256       847.20 -3.600000e-01    2.012292e-02
12    page_pool_put_unrefed_page    -1      303            1943751      6415.02  6.960000e+00    2.412866e-06
```

```
------- 2025-10-06-19-09-36-6.12.9-iommufd-no-writel-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores Run Metrics -------
Throughput: 278.491
CPU Util: 99.8200625
Drop rate: 0.0007358606
Acks per page: 0.04088521947782873
Per page stats:
        IOTLB Miss: 1.3003971434049932
        IOTLB First Lookup: 11.068191231112015
        IOTLB All Lookups: 19.45128046858109
        IOTLB Inv: 0.0
        IOMMU Mem Access: 2.6470694707678737
        PWT Occupancy: 2025183414.0
Reading eBPF stats from ../utils/reports/2025-10-06-19-09-36-6.12.9-iommufd-no-writel-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns     mean_ns   variance_us  count_per_page
0                      iommu_map    -1   3329559        45403674725    13636.54  2.746000e+01        0.019588
1                    __iommu_map    -1   3325899         6733381585     2024.53 -7.300000e-01        0.019567
2     intel_iommu_iotlb_sync_map    -1   3322760        27883185261     8391.57  2.163000e+01        0.019548
3       cache_tag_flush_range_np    -1   3319157        21978534541     6621.72  2.141000e+01        0.019527
4       iommu_flush_write_buffer    -1   3315799         3343987221     1008.50  8.000000e-02        0.019507
5                  __iommu_unmap    -1   3249278         7903708504     2432.45 -1.290000e+00        0.019116
6           intel_iommu_tlb_sync    -1   3246832        26718261701     8229.03  2.330000e+01        0.019102
7          cache_tag_flush_range    -1   3242299        19393264953     5981.33  2.494000e+01        0.019075
8           qi_batch_flush_descs    -1   5800249         5479981052      944.78  1.300000e-01        0.034124
9   page_pool_put_unrefed_netmem    -1  92422315       169904140855     1838.35 -2.500000e-01        0.543733
10    page_pool_put_unrefed_page    -1   1331792      4311900421260  3237668.06  6.647313e+11        0.007835
```

```
------- 2025-10-06-19-14-32-6.12.9-iommufd-no-writel-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores Run Metrics -------
Throughput: 336.996
CPU Util: 99.9726
Drop rate: 0.0041669753
Acks per page: 0.046164218162826856
Per page stats:
        IOTLB Miss: 1.2341563189117972
        IOTLB First Lookup: 10.724418027914776
        IOTLB All Lookups: 15.919911099616042
        IOTLB Inv: 0.0
        IOMMU Mem Access: 2.459357086910278
        PWT Occupancy: 2153650287.471
Reading eBPF stats from ../utils/reports/2025-10-06-19-14-32-6.12.9-iommufd-no-writel-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores-RUN-0/ebpf_guest_stats.csv
                        function  type      count  total_duration_ns      mean_ns   variance_us  count_per_page
0                      iommu_map    -1    2607288        36804723226     14116.09  2.065000e+01    1.267606e-02
1                    __iommu_map    -1    2605760         4287388675      1645.35 -4.700000e-01    1.266863e-02
2     intel_iommu_iotlb_sync_map    -1    2604083        24999873800      9600.26  1.854000e+01    1.266048e-02
3       cache_tag_flush_range_np    -1    2602529        21020720067      8077.04  1.790000e+01    1.265292e-02
4       iommu_flush_write_buffer    -1    2601087         2746740823      1056.00 -3.000000e-02    1.264591e-02
5                  __iommu_unmap    -1    2595622         5441798798      2096.53 -4.400000e-01    1.261934e-02
6           intel_iommu_tlb_sync    -1    2594481        23519480632      9065.20  1.952000e+01    1.261379e-02
7          cache_tag_flush_range    -1    2593531        18116546724      6985.28  2.009000e+01    1.260917e-02
8     page_pool_alloc_pages_slow    -1         45           87239310   1938651.33  4.671771e+05    2.187800e-07
9           qi_batch_flush_descs    -1    5183264         5424998540      1046.64  7.000000e-02    2.519988e-02
10             page_pool_dma_map    -1       2880           80664075     28008.36  1.181200e+02    1.400192e-05
11  page_pool_put_unrefed_netmem    -1  108245673       162471196035      1500.95  2.400000e-01    5.262665e-01
12    page_pool_put_unrefed_page    -1     163198     12157466225118  74495191.27  3.622500e+13    7.934326e-04
```