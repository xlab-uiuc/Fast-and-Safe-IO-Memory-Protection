#!/bin/bash

kernel="6.12.9"
iommu="off"

grub_src="grub_linux/grub_linux_${kernel}_${iommu}"
if [ -f $grub_src ]; then
#   echo "File does not exist."
    sudo cp $grub_src /etc/default/grub
else
    echo "$grub_src doesn't exist"
    exit 1
fi


sudo update-grub2

echo "Reboot to ${kernel} IOMMU=${iommu} in 10 seconds."

sudo reboot