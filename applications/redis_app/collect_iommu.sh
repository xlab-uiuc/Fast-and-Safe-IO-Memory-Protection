sudo rm logs/iommu.csv > /dev/null
sudo rm pcie.rpt > /dev/null
sudo taskset -c 31 ~/pcm/build/bin/pcm-iio 1 -csv=logs/iommu.csv > /dev/null 2>&1 &
sleep 5 
sudo pkill -9 -f "pcm" > /dev/null 2>&1
echo "IOTLB_hits: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $8; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
echo "IOTLB_misses: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $9; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
echo "CTXT_Miss: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $10; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
echo "L1_Miss: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $11; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
echo "L2_Miss: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $12; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
echo "L3_Miss: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $13; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
echo "Mem_Read: " $(cat logs/iommu.csv | grep "Socket0,IIO Stack 2 - PCIe1,Part0" | awk -F ',' '{ sum += $14; n++ } END { if (n > 0) printf "%0.3f", sum / n; }') >> pcie.rpt
cat pcie.rpt
