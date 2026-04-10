#!/bin/bash

SUB_DIR="reports"
DRY_RUN="true"

# Set the year and month threshold (YYYY-MM format)
# Only directories from this month and earlier will be compressed
YEAR_MONTH="2025-12"

THRESHOLD=$(echo "$YEAR_MONTH" | tr -d '-')

echo "Compressing directories in $SUB_DIR"
echo "Threshold: $YEAR_MONTH and earlier"
echo "Dry run mode: $DRY_RUN"
echo ""

if [[ "$DRY_RUN" != "true" ]]; then
    echo "WARNING: This will compress and DELETE directories!"
    echo "Press Ctrl+C within 3 seconds to cancel..."
    for i in 3 2 1; do
        echo "    $i..."
        sleep 1
    done
    echo "    Proceeding with compression and deletion."
    echo ""
fi

cd $SUB_DIR
declare -A groups

# Find all directories matching the pattern
for dir in */; do
    dir=${dir%/}
    
    if [[ ! -d "$dir" ]]; then
        continue
    fi
    
    if [[ "$dir" == *.tar.gz ]] || [[ "$dir" == *.tgz ]] || [[ "$dir" == *.tar ]]; then
        continue
    fi

    # Skip directories that don't start with a timestamp (YYYY-MM-DD)
    if [[ ! "$dir" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}- ]]; then
        continue
    fi
    
    if [[ "$dir" =~ flow[0-9]+ ]] && [[ "$dir" =~ ringbuf ]]; then
        dir_year_month=$(echo "$dir" | cut -d'-' -f1,2)
        dir_threshold=$(echo "$dir_year_month" | tr -d '-')
        
        if [[ "$dir_threshold" -le "$THRESHOLD" ]]; then
            # Extract prefix before "flow"
            prefix=$(echo "$dir" | sed 's/\(.*\)-flow[0-9]\+.*/\1/')
            # Extract the part between "flowNN" and "ringbuf"
            middle=$(echo "$dir" | sed 's/.*flow[0-9]\+\(.*\)-ringbuf.*/\1/')
            
            key="${prefix}${middle}"
            
            if [[ -z "${groups[$key]}" ]]; then
                groups[$key]="$dir"
            else
                groups[$key]="${groups[$key]} $dir"
            fi
        fi
    fi
done

for key in "${!groups[@]}"; do
    archive_name="${key}.tar.gz"
    dirs=${groups[$key]}

    dir_count=$(echo $dirs | wc -w)

    # Only compress if there are more than 2 directories
    if [[ $dir_count -le 2 ]]; then
        echo "[SKIPPED] $key only $dir_count count - need more than 2 to compress"
        echo ""
        continue
    fi
    
    echo "Creating archive: $archive_name"
    echo "Directories to compress ($dir_count): $dirs"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would create $archive_name and delete source directories"
        echo ""
    else
        tar -czvf "$archive_name" $dirs

        if [ $? -eq 0 ]; then
            echo "Successfully created $archive_name"
            for dir in $dirs; do
                echo "Deleting $dir"
                rm -rf "$dir"
            done
            echo ""
        else
            echo "ERROR: Failed to create $archive_name. Directories NOT deleted."
            echo ""
        fi
    fi
done
echo "Compression complete!"
