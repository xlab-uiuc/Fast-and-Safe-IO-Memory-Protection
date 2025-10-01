
Guest: nested, Host: IOMMU strict, 1 flow, 1 core
```
2025-10-01-00-54-16-6.12.9-iommufd-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores
------- 2025-10-01-00-54-16-6.12.9-iommufd-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores Run Metrics -------
Throughput: 47.327
CPU Util: 96.553
Drop rate: 1.05473e-05
Acks per page: 0.013117516377543475
Per page stats:
	IOTLB Miss: 0.9626571511967377
	IOTLB First Lookup: 9.73168538117117
	IOTLB All Lookups: 17.36657643530602
	IOTLB Inv: 0.06709783378452046
	IOMMU Mem Access: 2.0126289778496
	PWT Occupancy: 244667070.765
Reading eBPF stats from ../utils/reports/2025-10-01-00-54-16-6.12.9-iommufd-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores-RUN-0/ebpf_guest_stats.csv
                     function  core   count  total_duration_ns   mean_ns  variance_us  count_per_page
0                   iommu_map    -1  402547         2031055469   5045.51        -3.05        0.013936
1                 __iommu_map    -1  402504          345410705    858.15        -0.42        0.013934
2  intel_iommu_iotlb_sync_map    -1  402432         1179963605   2932.08        -2.14        0.013932
3    cache_tag_flush_range_np    -1  402374          853094041   2120.15        -2.13        0.013930
4    iommu_flush_write_buffer    -1  402309          183279666    455.57        -0.19        0.013927
5               __iommu_unmap    -1  402182          351020983    872.79        -0.54        0.013923
6        intel_iommu_tlb_sync    -1  402120         4058898878  10093.75       204.86        0.013921
7       cache_tag_flush_range    -1  402059         3717512149   9246.19       203.26        0.013919
8              qi_submit_sync    -1  401857         2796307307   6958.46       200.48        0.013912
9        qi_batch_flush_descs    -1  803590         3514784081   4373.85       115.74        0.027819
```

Guest: nested, Host: IOMMU strict, 2 flows, 2 cores
```
2025-10-01-00-54-16-6.12.9-iommufd-flow02-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_2cores
------- 2025-10-01-00-54-16-6.12.9-iommufd-flow02-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_2cores Run Metrics -------
Throughput: 84.254
CPU Util: 96.39375
Drop rate: 2.051e-06
Acks per page: 0.01634485528046146
Per page stats:
	IOTLB Miss: 1.1888580932893393
	IOTLB First Lookup: 10.317717071327367
	IOTLB All Lookups: 19.49365202345745
	IOTLB Inv: 0.08021441887169749
	IOMMU Mem Access: 2.4629945281602774
	PWT Occupancy: 516736338.312
Reading eBPF stats from ../utils/reports/2025-10-01-00-54-16-6.12.9-iommufd-flow02-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_2cores-RUN-0/ebpf_guest_stats.csv
                     function  core    count  total_duration_ns       mean_ns   variance_us  count_per_page
0                   iommu_map    -1   619831         5562251554  8.973820e+03  1.084400e+02        0.012053
1                 __iommu_map    -1   619821          782490915  1.262450e+03 -5.700000e-01        0.012053
2  intel_iommu_iotlb_sync_map    -1   619658         3142669026  5.071620e+03  1.068400e+02        0.012050
3    cache_tag_flush_range_np    -1   619550         2458996189  3.969000e+03  1.058100e+02        0.012048
4    iommu_flush_write_buffer    -1   619497          377431876  6.092600e+02 -8.000000e-02        0.012047
5               __iommu_unmap    -1   619088          924231345  1.492890e+03 -6.000000e-01        0.012039
6        intel_iommu_tlb_sync    -1   617695     91520789867868  1.481650e+08  2.103256e+13        0.012012
7       cache_tag_flush_range    -1   617679     91520031105279  1.481676e+08  2.103310e+13        0.012011
8              qi_submit_sync    -1   618645         5058304785  8.176430e+03  1.470900e+02        0.012030
9        qi_batch_flush_descs    -1  1237061         6503344723  5.257090e+03  9.536000e+01        0.024056
```

Guest: nested, Host: IOMMU strict, 4 flows, 4 cores
```
2025-10-01-00-54-16-6.12.9-iommufd-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores
------- 2025-10-01-00-54-16-6.12.9-iommufd-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores Run Metrics -------
Throughput: 155.808
CPU Util: 99.00675
Drop rate: 3.2296e-06
Acks per page: 0.014969107085643871
Per page stats:
	IOTLB Miss: 1.1825398632787019
	IOTLB First Lookup: 10.275812498796467
	IOTLB All Lookups: 19.348514490860545
	IOTLB Inv: 0.09848626463914562
	IOMMU Mem Access: 2.460526119012528
	PWT Occupancy: 982525946.765
Reading eBPF stats from ../utils/reports/2025-10-01-00-54-16-6.12.9-iommufd-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores-RUN-0/ebpf_guest_stats.csv
                     function  core    count  total_duration_ns       mean_ns   variance_us  count_per_page
0                   iommu_map    -1  1263910      5602925148132  4.433010e+06  1.008924e+13        0.013291
1                 __iommu_map    -1  1236584         2025577854  1.638040e+03 -8.400000e-01        0.013003
2  intel_iommu_iotlb_sync_map    -1  1222996        11614771519  9.496980e+03  1.964800e+02        0.012860
3    cache_tag_flush_range_np    -1  1207106        10187519689  8.439620e+03  1.951200e+02        0.012693
4    iommu_flush_write_buffer    -1  1189565         1142617708  9.605300e+02  1.700000e-01        0.012509
5               __iommu_unmap    -1  1160640         1972908947  1.699850e+03 -6.900000e-01        0.012205
6        intel_iommu_tlb_sync    -1  1157544    357443740923888  3.087949e+08  3.262744e+12        0.012172
7       cache_tag_flush_range    -1  1154407    335103723447460  2.902821e+08  7.071990e+12        0.012139
8              qi_submit_sync    -1  1152523         8299085868  7.200800e+03  6.377000e+01        0.012119
9        qi_batch_flush_descs    -1  2302747        11669754088  5.067750e+03  5.152000e+01        0.024215
```

Guest: nested, Host: IOMMU strict, 8 flows, 8 cores

```
2025-10-01-00-54-16-6.12.9-iommufd-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores
------- 2025-10-01-00-54-16-6.12.9-iommufd-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores Run Metrics -------
Throughput: 237.778
CPU Util: 99.9751875
Drop rate: 1.9862e-06
Acks per page: 0.016972596946731828
Per page stats:
	IOTLB Miss: 1.169167436785573
	IOTLB First Lookup: 10.031069849222316
	IOTLB All Lookups: 18.044039793826105
	IOTLB Inv: 0.10443122172783016
	IOMMU Mem Access: 2.4104495066154144
	PWT Occupancy: 1494127193.562
Reading eBPF stats from ../utils/reports/2025-10-01-00-54-16-6.12.9-iommufd-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores-RUN-0/ebpf_guest_stats.csv
                     function  core    count  total_duration_ns   mean_ns  variance_us  count_per_page
0                   iommu_map    -1  1593276        44750750684  28087.26       534.17        0.010978
1                 __iommu_map    -1  1592891         1524050073    956.78        -0.55        0.010976
2  intel_iommu_iotlb_sync_map    -1  1592512        41077956333  25794.44       523.77        0.010973
3    cache_tag_flush_range_np    -1  1592154        39685792817  24925.85       520.48        0.010971
4    iommu_flush_write_buffer    -1  1591795          752698568    472.86        -0.21        0.010968
5               __iommu_unmap    -1  1591092         1524359547    958.06        -0.54        0.010963
6        intel_iommu_tlb_sync    -1  1590756        48657883413  30587.90       454.49        0.010961
7       cache_tag_flush_range    -1  1590419        47201238695  29678.49       449.92        0.010959
8              qi_submit_sync    -1  1589262        13053228764   8213.39        62.59        0.010951
9        qi_batch_flush_descs    -1  3177865        16212989070   5101.85        52.78        0.021897
```

Guest: nested, Host: IOMMU strict, 16 flows, 16 cores
```
2025-10-01-00-54-16-6.12.9-iommufd-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores
------- 2025-10-01-00-54-16-6.12.9-iommufd-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores Run Metrics -------
Throughput: 25.011
CPU Util: 100.0
Drop rate: 0.0011689287
Acks per page: 0.016710291247850943
Per page stats:
	IOTLB Miss: 1.1993538689376675
	IOTLB First Lookup: 10.406633226020551
	IOTLB All Lookups: 19.501434221407223
	IOTLB Inv: 0.11009021502538884
	IOMMU Mem Access: 2.419536891127904
	PWT Occupancy: 302118861.5
Reading eBPF stats from ../utils/reports/2025-10-01-00-54-16-6.12.9-iommufd-flow16-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_16cores-RUN-0/ebpf_guest_stats.csv
                     function  core   count  total_duration_ns     mean_ns  variance_us  count_per_page
0                   iommu_map    -1  168369       172044605649  1021830.66   2421459.49        0.011029
1                 __iommu_map    -1  168218          715666900     4254.40        -0.38        0.011019
2  intel_iommu_iotlb_sync_map    -1  167998       169782742602  1010623.59   2422364.79        0.011005
3    cache_tag_flush_range_np    -1  167810       168911425313  1006563.53   2421388.00        0.010993
4    iommu_flush_write_buffer    -1  167599          612581640     3655.04         4.44        0.010979
5               __iommu_unmap    -1  167240          666866483     3987.48        -0.55        0.010955
6        intel_iommu_tlb_sync    -1  167034       112756086984   675048.71   1658099.43        0.010942
7       cache_tag_flush_range    -1  166887       111870746845   670338.29   1657284.25        0.010932
8              qi_submit_sync    -1  166287        11452454342    68871.62      1978.56        0.010893
9        qi_batch_flush_descs    -1  332209        13302755677    40043.33      2512.97        0.021762
```

Guest: nested, Host: IOMMU strict, 20 flows, 20 cores

```
2025-10-01-00-54-16-6.12.9-iommufd-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores
------- 2025-10-01-00-54-16-6.12.9-iommufd-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores Run Metrics -------
Throughput: 17.854
CPU Util: 100.0
Drop rate: 0.0130957671
Acks per page: 0.01978358364512154
Per page stats:
	IOTLB Miss: 1.1916301879690825
	IOTLB First Lookup: 10.292118698800493
	IOTLB All Lookups: 18.76966362811605
	IOTLB Inv: 0.10961801185258205
	IOMMU Mem Access: 2.326166553579926
	PWT Occupancy: 234720881.062
Reading eBPF stats from ../utils/reports/2025-10-01-00-54-16-6.12.9-iommufd-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores-RUN-0/ebpf_guest_stats.csv
                     function  core   count  total_duration_ns     mean_ns  variance_us  count_per_page
0                   iommu_map    -1  508784       608008784859  1195023.40   3968899.62        0.046689
1                 __iommu_map    -1  482088         2028471432     4207.68        -0.71        0.044240
2  intel_iommu_iotlb_sync_map    -1  450943       548705327923  1216795.31   4091493.39        0.041381
3    cache_tag_flush_range_np    -1  428459       524910678888  1225112.97   4143307.92        0.039318
4    iommu_flush_write_buffer    -1  400177         1516995295     3790.81         4.79        0.036723
5               __iommu_unmap    -1  335786         1360480313     4051.63        -0.32        0.030814
6        intel_iommu_tlb_sync    -1  303917       215843950294   710206.90   2549661.85        0.027889
7       cache_tag_flush_range    -1  266680       193414365879   725267.61   2662819.40        0.024472
8              qi_submit_sync    -1  191100        13457819748    70422.92      2731.85        0.017537
9        qi_batch_flush_descs    -1  338803        13833605609    40830.82      2937.44        0.031091
```

