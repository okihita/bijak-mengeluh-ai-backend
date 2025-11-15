#!/bin/bash
# Monitor DKI scraper progress

TARGET=90
REGION="ap-southeast-2"

while true; do
    # Check if process is running
    if ! ps aux | grep -q "[s]crape_dki_agencies.py"; then
        echo ""
        echo "🎉 SCRAPER FINISHED!"
        
        # Get final count
        COUNT=$(aws dynamodb scan --table-name agencies --region $REGION \
                --filter-expression "attribute_not_exists(keyword)" \
                --select COUNT 2>/dev/null | grep '"Count"' | awk '{print $2}' | tr -d ',')
        
        echo "✅ Total agencies scraped: $COUNT"
        
        if [ -f "dki_agencies.json" ]; then
            echo "📁 Output file: dki_agencies.json"
        fi
        
        exit 0
    fi
    
    # Get current count
    COUNT=$(aws dynamodb scan --table-name agencies --region $REGION \
            --filter-expression "attribute_not_exists(keyword)" \
            --select COUNT 2>/dev/null | grep '"Count"' | awk '{print $2}' | tr -d ',')
    
    PERCENT=$((COUNT * 100 / TARGET))
    
    # Progress bar
    FILLED=$((PERCENT / 2))
    BAR=$(printf '%*s' $FILLED | tr ' ' '█')
    EMPTY=$(printf '%*s' $((50 - FILLED)) | tr ' ' '░')
    
    echo -ne "\r🔄 Progress: [$BAR$EMPTY] $COUNT/$TARGET ($PERCENT%) "
    
    sleep 5
done
