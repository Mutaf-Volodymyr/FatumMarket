/**
 * Price formatter utility
 * Formats prices with thousands separator (space) and supports Ukrainian locale (comma as decimal separator)
 */

(function() {
    'use strict';

    /**
     * Format price with thousands separator
     * @param {number|string} price - Price value (number or string)
     * @param {number} decimals - Number of decimal places (default: 2)
     * @param {string} decimalSeparator - Decimal separator (default: ',')
     * @param {string} thousandsSeparator - Thousands separator (default: ' ')
     * @returns {string} Formatted price string
     */
    window.formatPrice = function(price, decimals = 2, decimalSeparator = ',', thousandsSeparator = ' ') {
        // Convert to number if string
        const numPrice = typeof price === 'string' ? parseFloat(price.replace(',', '.')) : price;
        
        if (isNaN(numPrice)) {
            return '0' + decimalSeparator + '00';
        }
        
        // Format with decimals
        const formatted = numPrice.toFixed(decimals);
        const parts = formatted.split('.');
        
        // Add thousands separator to integer part
        const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandsSeparator);
        
        // Combine with decimal part
        return parts.length > 1 ? `${integerPart}${decimalSeparator}${parts[1]}` : integerPart;
    };

    /**
     * Format price element text content
     * Extracts price from text, formats it, and updates the element
     * @param {HTMLElement} element - Element containing price
     * @param {boolean} preserveCurrency - Whether to preserve currency symbol (default: true)
     */
    window.formatPriceElement = function(element, preserveCurrency = true) {
        if (!element) return;
        
        const text = element.textContent || element.innerText;
        // Match price pattern: numbers with optional comma/dot and spaces, optional currency symbol
        // Remove spaces first, then match
        const cleanText = text.replace(/\s/g, '');
        const match = cleanText.match(/([\d.,]+)\s*([₴$€]?)/);
        
        if (match) {
            // Remove spaces and replace comma with dot for parsing
            const priceStr = match[1].replace(/\s/g, '').replace(',', '.');
            const currency = match[2] || '';
            const price = parseFloat(priceStr);
            
            if (!isNaN(price) && price >= 0) {
                const formattedPrice = window.formatPrice(price);
                const newText = preserveCurrency && currency 
                    ? `${formattedPrice} ${currency}` 
                    : formattedPrice;
                element.textContent = newText;
            }
        }
    };

    /**
     * Format all prices on the page
     * Finds all elements with price classes and formats them
     */
    window.formatAllPrices = function() {
        // Common price class names - exclude elements with data-price (formatted dynamically)
        const priceSelectors = [
            '.price-current:not([data-price])',
            '.price-old',
            '.cart-total-price',
            '.cart-total-discount',
            '.cart-final-price',
            '.cart-delivery-price',
            '.delivery-price',
            '.summary-item span:last-child',
            '.summary-total span:last-child'
        ];
        
        priceSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                // Skip if already formatted (contains space as thousands separator)
                const text = element.textContent || '';
                if (/\d\s+\d/.test(text)) {
                    return; // Already formatted
                }
                window.formatPriceElement(element);
            });
        });
    };

    // Auto-format prices when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.formatAllPrices);
    } else {
        window.formatAllPrices();
    }
})();

