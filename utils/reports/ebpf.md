Usage: python script.py <exp_name> <metrics>

1 flow & core
```
------- 2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores Run Metrics -------
Throughput: 46.913
CPU Util: 100.0
Drop rate: 6.9598e-06
Acks per page: 0.011157171172169762
Per page stats:
	IOTLB Miss: 1.0182934255241831
	IOTLB First Lookup: 9.992788985910089
	IOTLB All Lookups: 17.35123975836122
	IOTLB Inv: 0.07360253473450856
	IOMMU Mem Access: 1.9066415944407733
	PWT Occupancy: 221906394.188
Reading eBPF stats from ../utils/reports/2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores-RUN-0/ebpf_guest_stats.csv
                        function  type    count  total_duration_ns   mean_ns  variance_us  count_per_page
0                      iommu_map    -1   171036         1139456425   6662.09        -4.24        0.005973
1                    __iommu_map    -1   170998          185684984   1085.89        -0.69        0.005972
2     intel_iommu_iotlb_sync_map    -1   170922          686091943   4014.06        -3.05        0.005969
3       cache_tag_flush_range_np    -1   170866          498774037   2919.09        -2.03        0.005967
4       iommu_flush_write_buffer    -1   170811          118642694    694.58        -0.26        0.005965
5                  __iommu_unmap    -1   170698          186294285   1091.37        -0.74        0.005961
6           intel_iommu_tlb_sync    -1   170646         2118537135  12414.81       385.33        0.005960
7          cache_tag_flush_range    -1   170591         1922281964  11268.37       383.70        0.005958
8                 qi_submit_sync    -1   170362         1494422523   8772.04       378.01        0.005950
9           qi_batch_flush_descs    -1   340833         1807166455   5302.21       210.82        0.011903
10       trace_qi_submit_sync_cs    -1   170252         1294629687   7604.20       377.08        0.005946
11  page_pool_put_unrefed_netmem    -1  8695550         6395061571    735.44        -0.28        0.303685
12    page_pool_put_unrefed_page    -1      122             266038   2180.64        -1.07        0.000004

```

4 flow & core
```
------- 2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores Run Metrics -------
Throughput: 166.568
CPU Util: 100.0
Drop rate: 9.976e-07
Acks per page: 0.013932173862926852
Per page stats:
	IOTLB Miss: 1.14558250952327
	IOTLB First Lookup: 9.777568002791028
	IOTLB All Lookups: 18.448538498145528
	IOTLB Inv: 0.09115335522866337
	IOMMU Mem Access: 2.3182612214913787
	PWT Occupancy: 971250965.412
Reading eBPF stats from ../utils/reports/2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns   mean_ns  variance_us  count_per_page
0                      iommu_map    -1    648739         5528942156   8522.60       296.42        0.006381
1                    __iommu_map    -1    648502          641657150    989.45        -0.60        0.006379
2     intel_iommu_iotlb_sync_map    -1    648270         3902221495   6019.44       295.04        0.006377
3       cache_tag_flush_range_np    -1    648045         3295997260   5086.06       295.88        0.006374
4       iommu_flush_write_buffer    -1    647803          333835119    515.33        -0.23        0.006372
5                  __iommu_unmap    -1    647336          633511789    978.64        -0.54        0.006367
6           intel_iommu_tlb_sync    -1    647106         9527337524  14722.99       202.38        0.006365
7          cache_tag_flush_range    -1    646879         8864704505  13703.81       200.82        0.006363
8                 qi_submit_sync    -1    645893         6084550333   9420.37       122.24        0.006353
9           qi_batch_flush_descs    -1   1292238         7132626300   5519.59        86.35        0.012711
10       trace_qi_submit_sync_cs    -1    645454         5362290481   8307.78       121.02        0.006349
11  page_pool_put_unrefed_netmem    -1  37297328        20335614809    545.23        -0.21        0.366865
12    page_pool_put_unrefed_page    -1       775            1347659   1738.91        -1.12        0.000008
```

8 flow & core
```
------- 2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores Run Metrics -------
Throughput: 159.404
CPU Util: 99.8865
Drop rate: 2.9706e-06
Acks per page: 0.014431629178690623
Per page stats:
	IOTLB Miss: 1.1012391911871722
	IOTLB First Lookup: 9.37129735625204
	IOTLB All Lookups: 16.570158605605883
	IOTLB Inv: 0.11572329316463828
	IOMMU Mem Access: 2.2484629998745325
	PWT Occupancy: 894057325.062
Reading eBPF stats from ../utils/reports/2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns       mean_ns   variance_us  count_per_page
0                      iommu_map    -1   1788292      6183041804167  3.457512e+06  5.106689e+11        0.018381
1                    __iommu_map    -1   1752395         2227055514  1.270860e+03 -5.300000e-01        0.018012
2     intel_iommu_iotlb_sync_map    -1   1707617        27438328576  1.606820e+04  4.706800e+02        0.017551
3       cache_tag_flush_range_np    -1   1705916        25564375458  1.498572e+04  4.691400e+02        0.017534
4       iommu_flush_write_buffer    -1   1678465         1491011350  8.883200e+02  1.700000e-01        0.017252
5                  __iommu_unmap    -1   1627399         2557927152  1.571790e+03 -5.100000e-01        0.016727
6           intel_iommu_tlb_sync    -1   1570730        35766444256  2.277059e+04  2.908800e+02        0.016144
7          cache_tag_flush_range    -1   1570406        33464521935  2.130947e+04  2.929400e+02        0.016141
8                 qi_submit_sync    -1   1453295        12498719171  8.600260e+03  6.011000e+01        0.014937
9           qi_batch_flush_descs    -1   2971101        15873610964  5.342670e+03  5.162000e+01        0.030538
10       trace_qi_submit_sync_cs    -1   1392530        10196588233  7.322350e+03  6.028000e+01        0.014313
11  page_pool_put_unrefed_netmem    -1  56118048        57621406170  1.026790e+03  1.900000e-01        0.576797
12    page_pool_put_unrefed_page    -1     64079    246231280081725  3.842621e+09  3.379906e+13        0.000659
```

20 flow & core
```
------- 2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores Run Metrics -------
Throughput: 18.0
CPU Util: 99.99735
Drop rate: 0.0105981691
Acks per page: 0.02008469048888889
Per page stats:
	IOTLB Miss: 1.2731322131342222
	IOTLB First Lookup: 10.490504613432888
	IOTLB All Lookups: 18.781935896348443
	IOTLB Inv: 0.10933835639466667
	IOMMU Mem Access: 2.3686680758044445
	PWT Occupancy: 214887392.647
Reading eBPF stats from ../utils/reports/2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores-RUN-0/ebpf_guest_stats.csv
                        function  type     count  total_duration_ns     mean_ns  variance_us  count_per_page
0                      iommu_map    -1    657423       811346922685  1234132.24   4078555.49        0.059840
1                    __iommu_map    -1    629085         2667726698     4240.65        -0.39        0.057261
2     intel_iommu_iotlb_sync_map    -1    604227       752131135238  1244782.40   4167118.65        0.054998
3       cache_tag_flush_range_np    -1    580133       724976161891  1249672.34   4207074.99        0.052805
4       iommu_flush_write_buffer    -1    558943         2076529419     3715.10         3.58        0.050876
5                  __iommu_unmap    -1    499915         2036478252     4073.65        -0.81        0.045503
6           intel_iommu_tlb_sync    -1    473102       360266895752   761499.41   2695061.66        0.043063
7          cache_tag_flush_range    -1    450158       344191430438   764601.39   2727268.43        0.040974
8                 qi_submit_sync    -1    359073        27308442500    76052.62      2515.41        0.032684
9           qi_batch_flush_descs    -1    752523        31516145928    41880.64      2880.87        0.068496
10       trace_qi_submit_sync_cs    -1    318545        22430274841    70414.78      2367.43        0.028995
11  page_pool_put_unrefed_netmem    -1  12757594        26657209578     2089.52        -1.24        1.161225
12    page_pool_put_unrefed_page    -1      1239           11756313     9488.55        -1.85        0.000113
```

