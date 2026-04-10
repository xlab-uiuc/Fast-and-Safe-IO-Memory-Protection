
```
2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores
------- 2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores Run Metrics -------
Throughput: 33.777
CPU Util: 100.0
Drop rate: 1.13766e-05
Acks per page: 0.030273219859667824
Per page stats:
	IOTLB Miss: 0.6100415164553394
	IOTLB First Lookup: 9.274437391044557
	IOTLB All Lookups: 13.4962224235957
	IOTLB Inv: 0.19150809643579952
	IOMMU Mem Access: 1.2722873676965984
	PWT Occupancy: 107436801.353
Reading eBPF stats from ../utils/reports/2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns   mean_ns  variance_us  count_per_page
0                      iommu_map    -1    185965          640924744   3446.48         0.35        0.009020
1                    __iommu_map    -1    185923          154941223    833.36        -0.45        0.009018
2     intel_iommu_iotlb_sync_map    -1    185853          246528053   1326.47        -0.32        0.009015
3       cache_tag_flush_range_np    -1    185791           88213903    474.80        -0.21        0.009012
4                  __iommu_unmap    -1    185587          182778932    984.87        -0.41        0.009002
5           intel_iommu_tlb_sync    -1    185527         2242903899  12089.37       355.10        0.008999
6          cache_tag_flush_range    -1    185469         2055926487  11085.01       353.62        0.008996
7                 qi_submit_sync    -1    185214         1609447364   8689.66       346.07        0.008984
8           qi_batch_flush_descs    -1    185283         1791294457   9667.88       346.72        0.008987
9        trace_qi_submit_sync_cs    -1    185095         1430565528   7728.82       345.51        0.008978
10  page_pool_put_unrefed_netmem    -1  10875935         5188747098    477.09        -0.16        0.527552
11    page_pool_put_unrefed_page    -1       322             490917   1524.59        -0.86        0.000016
```

```
2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores
------- 2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores Run Metrics -------
Throughput: 153.819
CPU Util: 99.97525
Drop rate: 1.0829e-06
Acks per page: 0.017175458220375896
Per page stats:
	IOTLB Miss: 1.1499140474453742
	IOTLB First Lookup: 9.811289727068827
	IOTLB All Lookups: 18.258072435992954
	IOTLB Inv: 0.11088180014172501
	IOMMU Mem Access: 2.3453380875964607
	PWT Occupancy: 880284529.062
Reading eBPF stats from ../utils/reports/2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns   mean_ns  variance_us  count_per_page
0                      iommu_map    -1    722850         2635303813   3645.71         0.25        0.007699
1                    __iommu_map    -1    722652          677524944    937.55        -0.54        0.007697
2     intel_iommu_iotlb_sync_map    -1    722426          986897501   1366.09        -0.33        0.007695
3       cache_tag_flush_range_np    -1    722210          361248452    500.20        -0.22        0.007693
4                  __iommu_unmap    -1    721489          644919374    893.87        -0.48        0.007685
5           intel_iommu_tlb_sync    -1    721270        11242682556  15587.34       566.26        0.007683
6          cache_tag_flush_range    -1    721054        10572805730  14662.99       563.98        0.007680
7                 qi_submit_sync    -1    720078         6945888032   9646.02       144.09        0.007670
8           qi_batch_flush_descs    -1    720285         7646620349  10616.10       147.27        0.007672
9        trace_qi_submit_sync_cs    -1    719617         6200236332   8616.02       142.65        0.007665
10  page_pool_put_unrefed_netmem    -1  40070637        19987890456    498.82        -0.18        0.426812
11    page_pool_put_unrefed_page    -1      6022            7852840   1304.03        -0.61        0.000064
```
```
2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores
------- 2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores Run Metrics -------
Throughput: 252.115
CPU Util: 99.98775
Drop rate: 6.649e-07
Acks per page: 0.016678686497828374
Per page stats:
	IOTLB Miss: 1.1757468204891262
	IOTLB First Lookup: 9.735756925468076
	IOTLB All Lookups: 18.046871112246397
	IOTLB Inv: 0.1095388821133213
	IOMMU Mem Access: 2.391131853955536
	PWT Occupancy: 1533534976.375
Reading eBPF stats from ../utils/reports/2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns       mean_ns   variance_us  count_per_page
0                      iommu_map    -1   1092967         7100356604  6.496410e+03  2.270000e+00        0.007103
1                    __iommu_map    -1   1092570         1736365257  1.589250e+03 -6.600000e-01        0.007100
2     intel_iommu_iotlb_sync_map    -1   1092176         2860565448  2.619140e+03 -9.000000e-02        0.007098
3       cache_tag_flush_range_np    -1   1091771         1190819447  1.090720e+03  1.500000e-01        0.007095
4                  __iommu_unmap    -1   1090475         1994403509  1.828930e+03 -8.500000e-01        0.007087
5           intel_iommu_tlb_sync    -1   1090061        30123622708  2.763480e+04  1.028200e+03        0.007084
6          cache_tag_flush_range    -1   1089638        28168127312  2.585090e+04  1.032220e+03        0.007081
7                 qi_submit_sync    -1   1087853        11577580347  1.064260e+04  1.053200e+02        0.007070
8           qi_batch_flush_descs    -1   1088263        13630305155  1.252483e+04  1.047500e+02        0.007072
9        trace_qi_submit_sync_cs    -1   1087121         9832391614  9.044430e+03  1.046100e+02        0.007065
10  page_pool_put_unrefed_netmem    -1  47688962        59111728008  1.239530e+03  3.600000e-01        0.309913
11    page_pool_put_unrefed_page    -1     48911      5586076335011  1.142090e+08  1.063145e+14        0.000318
```

```
2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores
------- 2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores Run Metrics -------
Throughput: 32.966
CPU Util: 100.0
Drop rate: 0.0033811853
Acks per page: 0.017448815870897288
Per page stats:
	IOTLB Miss: 1.162521051253291
	IOTLB First Lookup: 9.973923076612753
	IOTLB All Lookups: 18.512692914639324
	IOTLB Inv: 0.09580553492640902
	IOMMU Mem Access: 2.338268557908148
	PWT Occupancy: 373632677.125
Reading eBPF stats from ../utils/reports/2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns    mean_ns  variance_us  count_per_page
0                      iommu_map    -1    977974        16209789238   16574.87        18.81        0.048605
1                    __iommu_map    -1    941659         3587684102    3809.96        -0.08        0.046800
2     intel_iommu_iotlb_sync_map    -1    908413         5957618295    6558.27        -1.48        0.045148
3       cache_tag_flush_range_np    -1    882626         2304886770    2611.40         0.21        0.043866
4                  __iommu_unmap    -1    776352         2611790623    3364.18        -0.38        0.038584
5           intel_iommu_tlb_sync    -1    744850       576992512879  774642.56   1626457.60        0.037019
6          cache_tag_flush_range    -1    708345       552500163230  779987.38   1649900.32        0.035205
7                 qi_submit_sync    -1    560644        32970628092   58808.49      2006.08        0.027864
8           qi_batch_flush_descs    -1    590359        37750470975   63944.94      2183.71        0.029341
9        trace_qi_submit_sync_cs    -1    497435        26742357382   53760.51      1873.72        0.024722
10  page_pool_put_unrefed_netmem    -1  22522391        42723491010    1896.93        -1.35        1.119356
11    page_pool_put_unrefed_page    -1       308            2646665    8593.07         2.52        0.000015
```

```
2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores
------- 2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores Run Metrics -------
Throughput: 36.873
CPU Util: 99.996875
Drop rate: 0.0219449664
Acks per page: 0.017521011298239905
Per page stats:
	IOTLB Miss: 1.204611738226236
	IOTLB First Lookup: 10.431303739429936
	IOTLB All Lookups: 19.380203838255635
	IOTLB Inv: 0.10309438602771676
	IOMMU Mem Access: 2.46238960843978
	PWT Occupancy: 472869746.188
Reading eBPF stats from ../utils/reports/2025-10-12-22-13-10-6.12.9-iommufd-no-map-contention-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns     mean_ns  variance_us  count_per_page
0                      iommu_map    -1   1170110        19258201417    16458.45        14.03        0.051992
1                    __iommu_map    -1   1126872         4284106435     3801.77         0.14        0.050071
2     intel_iommu_iotlb_sync_map    -1   1077658         7001216264     6496.70        -2.80        0.047884
3       cache_tag_flush_range_np    -1   1036637         2659680166     2565.68        -0.02        0.046062
4                  __iommu_unmap    -1    907219         3121130760     3440.33         0.06        0.040311
5           intel_iommu_tlb_sync    -1    861812       890860506358  1033706.31   3577537.57        0.038293
6          cache_tag_flush_range    -1    815331       849000933555  1041296.03   3615449.43        0.036228
7                 qi_submit_sync    -1    626149        36882805549    58904.20      2335.95        0.027822
8           qi_batch_flush_descs    -1    673511        42958388261    63782.76      2504.17        0.029927
9        trace_qi_submit_sync_cs    -1    544099        29367935240    53975.35      2217.12        0.024176
10  page_pool_put_unrefed_netmem    -1  22786117        45765700956     2008.49        -1.64        1.012469
11    page_pool_put_unrefed_page    -1      1049            8903164     8487.29        -4.08        0.000047
```
