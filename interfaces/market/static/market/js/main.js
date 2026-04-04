// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    function showAlert(message, type = 'info', timeout = 4500) {
        if (!message) return;
        let container = document.querySelector('.alert-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'alert-container';
            container.setAttribute('role', 'status');
            container.setAttribute('aria-live', 'polite');
            document.body.appendChild(container);
        }

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        alert.dataset.alertTimeout = timeout;
        container.appendChild(alert);

        requestAnimationFrame(() => {
            alert.classList.add('is-visible');
        });

        window.setTimeout(() => {
            alert.classList.add('is-hide');
            window.setTimeout(() => {
                alert.remove();
            }, 300);
        }, timeout);
    }

    function updateCartBadge(cartCount) {
        const cartBadge = document.querySelector('.navbar-link-cart .cart-badge');
        const cartLink = document.querySelector('.navbar-link-cart');
        if (!cartLink) return;

        if (cartCount > 0) {
            if (cartBadge) {
                cartBadge.textContent = cartCount;
            } else {
                const badge = document.createElement('span');
                badge.className = 'cart-badge';
                badge.textContent = cartCount;
                cartLink.appendChild(badge);
            }
        } else if (cartBadge) {
            cartBadge.remove();
        }
    }

    function updateCartTotals(data) {
        const totalPriceEl = document.querySelector('.cart-total-price');
        const totalDiscountEl = document.querySelector('.cart-total-discount');
        const discountSection = totalDiscountEl ? totalDiscountEl.closest('.cart-summary-item.discount') : null;

        if (totalPriceEl && data.total_price !== undefined) {
            totalPriceEl.textContent = `${window.formatPrice(parseFloat(data.total_price))} ₴`;
        }

        const totalDiscount = parseFloat(data.total_discount || 0);
        if (totalDiscount > 0) {
            if (totalDiscountEl) {
                totalDiscountEl.textContent = `-${window.formatPrice(totalDiscount)} ₴`;
            }
            if (discountSection) {
                discountSection.style.display = '';
            }
        } else if (discountSection) {
            discountSection.style.display = 'none';
        }

        const finalPriceEl = document.querySelector('#finalPrice');
        if (finalPriceEl && data.final_price !== undefined) {
            finalPriceEl.textContent = `${window.formatPrice(parseFloat(data.final_price))} ₴`;
        }
    }

    function showEmptyCartState() {
        const cartForm = document.querySelector('.cart-form');
        const container = document.querySelector('.container');
        if (!container || !cartForm) return;

        cartForm.classList.add('is-removing');
        window.setTimeout(() => {
            cartForm.remove();
            const homeUrl = document.querySelector('.navbar-logo')?.getAttribute('href') || '/';
            const empty = document.createElement('div');
            empty.className = 'empty-cart';
            empty.innerHTML = `
                <p>Ваша корзина пуста</p>
                <a href="${homeUrl}" class="btn btn-primary">Перейти к товарам</a>
            `;
            container.appendChild(empty);
        }, 260);
    }

    function removeCartItemById(itemId, removeUrl) {
        if (!removeUrl || !itemId) return;
        const csrfToken = document.querySelector('#cartForm input[name="csrfmiddlewaretoken"]')?.value ||
                         document.querySelector('form input[name="csrfmiddlewaretoken"]')?.value;
        fetch(removeUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {})
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                showAlert(data.error || 'Не удалось удалить товар', 'error');
                return;
            }

            const items = document.querySelectorAll(`.cart-item[data-item-id="${itemId}"]`);
            items.forEach(cartItem => {
                cartItem.classList.add('is-removing');
            });

            window.setTimeout(() => {
                items.forEach(cartItem => cartItem.remove());
                updateCartTotals(data);
                updateCartBadge(parseInt(data.cart_count, 10) || 0);
                if (data.empty) {
                    showEmptyCartState();
                }
            }, 260);

            showAlert(data.message || 'Товар удален из корзины', 'success');
        })
        .catch(() => {
            showAlert('Не удалось удалить товар', 'error');
        });
    }

    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            requestAnimationFrame(() => {
                alert.classList.add('is-visible');
            });

            const timeout = parseInt(alert.dataset.alertTimeout, 10) || 4500;
            window.setTimeout(() => {
                alert.classList.add('is-hide');
                window.setTimeout(() => {
                    alert.remove();
                }, 300);
            }, timeout);
        });
    }
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
        });
    }
    
    // Categories and Brands dropdown toggle
    const categoriesBrandsToggle = document.getElementById('categoriesBrandsToggle');
    const categoriesBrandsDropdown = document.getElementById('categoriesBrandsDropdown');
    
    if (categoriesBrandsToggle && categoriesBrandsDropdown) {
        categoriesBrandsToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            categoriesBrandsDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!categoriesBrandsToggle.contains(e.target) && !categoriesBrandsDropdown.contains(e.target)) {
                categoriesBrandsDropdown.classList.remove('show');
            }
        });
    }
    
    // Product filters mobile toggle
    const filtersToggleMobile = document.getElementById('filtersToggleMobile');
    const filtersSidebar = document.getElementById('productsFiltersSidebar');
    const filtersClose = document.getElementById('filtersClose');
    
    if (filtersToggleMobile && filtersSidebar) {
        filtersToggleMobile.addEventListener('click', function() {
            filtersSidebar.classList.add('show');
        });
        
        if (filtersClose) {
            filtersClose.addEventListener('click', function() {
                filtersSidebar.classList.remove('show');
            });
        }
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (filtersSidebar.classList.contains('show') && 
                    !filtersSidebar.contains(e.target) && 
                    !filtersToggleMobile.contains(e.target)) {
                    filtersSidebar.classList.remove('show');
                }
            }
        });
    }
    
    // Dual range slider for price
    const minPriceSlider = document.getElementById('min_price_slider');
    const maxPriceSlider = document.getElementById('max_price_slider');
    const minPriceInput = document.getElementById('min_price');
    const maxPriceInput = document.getElementById('max_price');
    const dualRangeWrapper = document.querySelector('.dual-range-wrapper');
    
    function updateDualRangeFill() {
        if (!minPriceSlider || !maxPriceSlider || !dualRangeWrapper) return;
        
        const min = parseFloat(minPriceSlider.min);
        const max = parseFloat(minPriceSlider.max);
        const minVal = parseFloat(minPriceSlider.value);
        const maxVal = parseFloat(maxPriceSlider.value);
        
        const percentMin = ((minVal - min) / (max - min)) * 100;
        const percentMax = ((maxVal - min) / (max - min)) * 100;
        
        dualRangeWrapper.style.setProperty('--range-left', percentMin + '%');
        dualRangeWrapper.style.setProperty('--range-right', (100 - percentMax) + '%');
    }
    
    if (minPriceSlider && maxPriceSlider && minPriceInput && maxPriceInput) {
        // Initialize
        updateDualRangeFill();
        
        // Sync sliders with inputs
        minPriceSlider.addEventListener('input', function() {
            const minVal = parseFloat(this.value);
            const maxVal = parseFloat(maxPriceSlider.value);
            const minLimit = parseFloat(this.min);
            
            if (minVal >= minLimit) {
                minPriceInput.value = Math.round(minVal);
                
                if (minVal > maxVal) {
                    maxPriceSlider.value = minVal;
                    maxPriceInput.value = Math.round(minVal);
                }
                
                updateDualRangeFill();
            }
        });
        
        maxPriceSlider.addEventListener('input', function() {
            const maxVal = parseFloat(this.value);
            const minVal = parseFloat(minPriceSlider.value);
            const maxLimit = parseFloat(this.max);
            
            if (maxVal <= maxLimit) {
                maxPriceInput.value = Math.round(maxVal);
                
                if (maxVal < minVal) {
                    minPriceSlider.value = maxVal;
                    minPriceInput.value = Math.round(maxVal);
                }
                
                updateDualRangeFill();
            }
        });
        
        // Sync inputs with sliders
        minPriceInput.addEventListener('input', function() {
            const value = parseFloat(this.value) || parseFloat(minPriceSlider.min);
            const minLimit = parseFloat(minPriceSlider.min);
            const maxLimit = parseFloat(maxPriceSlider.value);
            
            if (value >= minLimit && value <= maxLimit) {
                minPriceSlider.value = value;
                updateDualRangeFill();
            } else if (value < minLimit) {
                this.value = minLimit;
                minPriceSlider.value = minLimit;
                updateDualRangeFill();
            } else if (value > maxLimit) {
                this.value = maxLimit;
                minPriceSlider.value = maxLimit;
                updateDualRangeFill();
            }
        });
        
        maxPriceInput.addEventListener('input', function() {
            const value = parseFloat(this.value) || parseFloat(maxPriceSlider.max);
            const minLimit = parseFloat(minPriceSlider.value);
            const maxLimit = parseFloat(maxPriceSlider.max);
            
            if (value >= minLimit && value <= maxLimit) {
                maxPriceSlider.value = value;
                updateDualRangeFill();
            } else if (value < minLimit) {
                this.value = minLimit;
                maxPriceSlider.value = minLimit;
                updateDualRangeFill();
            } else if (value > maxLimit) {
                this.value = maxLimit;
                maxPriceSlider.value = maxLimit;
                updateDualRangeFill();
            }
        });
    }
    
    // Product card carousel
    const carousels = document.querySelectorAll('.product-card-carousel');
    carousels.forEach(carousel => {
        const slides = carousel.querySelectorAll('.carousel-slide');
        const dots = carousel.querySelectorAll('.carousel-dot');
        const prevBtn = carousel.querySelector('.carousel-prev');
        const nextBtn = carousel.querySelector('.carousel-next');
        let currentSlide = 0;
        
        if (slides.length <= 1) return;
        
        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
            if (dots.length > 0) {
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === index);
                });
            }
            currentSlide = index;
        }
        
        function nextSlide() {
            const next = (currentSlide + 1) % slides.length;
            showSlide(next);
        }
        
        function prevSlide() {
            const prev = (currentSlide - 1 + slides.length) % slides.length;
            showSlide(prev);
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                nextSlide();
            });
        }
        
        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                prevSlide();
            });
        }
        
        dots.forEach((dot, index) => {
            dot.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                showSlide(index);
            });
        });
        
        // Auto-rotate on hover (optional)
        let autoRotateInterval;
        const card = carousel.closest('.product-card');
        if (card) {
            card.addEventListener('mouseenter', () => {
                autoRotateInterval = setInterval(nextSlide, 3000);
            });
            card.addEventListener('mouseleave', () => {
                if (autoRotateInterval) {
                    clearInterval(autoRotateInterval);
                }
            });
        }
    });
    
    // Get cart URL from navbar
    const cartLink = document.querySelector('.navbar-link-cart');
    const cartUrl = cartLink ? cartLink.href : '/cart/';
    
    // AJAX cart add functionality
    const cartForms = document.querySelectorAll('.product-card-form, .product-add-form');
    cartForms.forEach(form => {
        const submitButton = form.querySelector('button[type="submit"]');
        
        // If button is already "in cart", make it redirect to cart
        if (submitButton && submitButton.classList.contains('btn-in-cart')) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                window.location.href = cartUrl;
            });
            return;
        }
        
        const handleSubmit = async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const productId = form.dataset.productId;
            const originalText = submitButton.textContent;
            const originalClasses = submitButton.className;
            
            // Disable button during request
            submitButton.disabled = true;
            submitButton.textContent = 'Добавление...';
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin'
                });
                
                // Handle redirect (non-JSON response, e.g., login required)
                if (!response.headers.get('content-type')?.includes('application/json')) {
                    // Redirect response (likely login required)
                    window.location.href = response.url || form.action;
                    return;
                }
                
                const data = await response.json();
                
                if (data.success) {
                    // Update button text and style with animation
                    submitButton.textContent = 'В корзине';
                    submitButton.className = submitButton.className.replace('btn-primary', 'btn-in-cart');
                    if (!submitButton.classList.contains('btn-in-cart')) {
                        submitButton.classList.add('btn-in-cart');
                    }
                    submitButton.classList.remove('btn-primary');
                    
                    // Update form behavior: now redirects to cart on click
                    form.removeEventListener('submit', handleSubmit);
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();
                        window.location.href = cartUrl;
                    });
                    
                    // Update cart count in navbar
                    const cartBadge = document.querySelector('.navbar-link-cart .cart-badge');
                    const currentCartLink = document.querySelector('.navbar-link-cart');
                    
                    if (data.cart_count > 0) {
                        if (cartBadge) {
                            cartBadge.textContent = data.cart_count;
                        } else if (currentCartLink) {
                            const badge = document.createElement('span');
                            badge.className = 'cart-badge';
                            badge.textContent = data.cart_count;
                            currentCartLink.appendChild(badge);
                        }
                    }
                    
                    // Update all buttons for this product on the page
                    const allButtonsForProduct = document.querySelectorAll(`.cart-button[data-product-id="${productId}"]`);
                    allButtonsForProduct.forEach(btn => {
                        btn.textContent = 'В корзине';
                        btn.className = btn.className.replace('btn-primary', 'btn-in-cart');
                        if (!btn.classList.contains('btn-in-cart')) {
                            btn.classList.add('btn-in-cart');
                        }
                        btn.classList.remove('btn-primary');
                        
                    });
                } else {
                    // Show error
                    showAlert(data.error || 'Ошибка при добавлении товара в корзину', 'error');
                    submitButton.textContent = originalText;
                    submitButton.className = originalClasses;
                }
            } catch (error) {
                console.error('Error adding to cart:', error);
                showAlert('Произошла ошибка при добавлении товара в корзину', 'error');
                submitButton.textContent = originalText;
                submitButton.className = originalClasses;
            } finally {
                submitButton.disabled = false;
            }
        };
        
        form.addEventListener('submit', handleSubmit);
    });
    
    // AJAX cart quantity update functionality
    const quantityForms = document.querySelectorAll('.quantity-form');
    quantityForms.forEach(form => {
        const quantityInput = form.querySelector('.quantity-input');
        if (!quantityInput) return;
        
        // Quantity button handlers
        const decreaseBtn = form.querySelector('.quantity-btn-decrease');
        const increaseBtn = form.querySelector('.quantity-btn-increase');
        
        function updateQuantityButtons() {
            const currentValue = parseInt(quantityInput.value) || 1;
            const min = parseInt(quantityInput.min) || 1;
            // Get max from input max attribute, data attribute, or form data attribute
            const maxFromInput = parseInt(quantityInput.max) || parseInt(quantityInput.dataset.max) || Infinity;
            const maxFromForm = parseInt(form.dataset.maxQuantity) || Infinity;
            const max = Math.min(maxFromInput, maxFromForm);
            
            // Update input max attribute if needed
            if (max !== Infinity && max !== parseInt(quantityInput.max)) {
                quantityInput.max = max;
                quantityInput.dataset.max = max;
            }
            
            if (decreaseBtn) {
                decreaseBtn.disabled = currentValue <= min;
            }
            if (increaseBtn) {
                increaseBtn.disabled = currentValue >= max;
            }
        }
        
        // Initialize button states
        updateQuantityButtons();
        
        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const currentValue = parseInt(quantityInput.value) || 1;
                const min = parseInt(quantityInput.min) || 1;
                if (currentValue > min) {
                    quantityInput.value = currentValue - 1;
                    updateQuantityButtons();
                    quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
        
        if (increaseBtn) {
            increaseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const currentValue = parseInt(quantityInput.value) || 1;
                const maxFromInput = parseInt(quantityInput.max) || parseInt(quantityInput.dataset.max) || Infinity;
                const maxFromForm = parseInt(form.dataset.maxQuantity) || Infinity;
                const max = Math.min(maxFromInput, maxFromForm);
                
                if (currentValue < max) {
                    quantityInput.value = currentValue + 1;
                    updateQuantityButtons();
                    quantityInput.dispatchEvent(new Event('change', { bubbles: true }));
                } else {
                    showAlert(`Доступно только ${max} шт. на складе`, 'warning');
                }
            });
        }
        
        quantityInput.addEventListener('change', function() {
            const currentValue = parseInt(quantityInput.value) || 1;
            const min = parseInt(quantityInput.min) || 1;
            const max = parseInt(quantityInput.max) || Infinity;
            
            // Validate quantity against available stock
            if (currentValue < min) {
                quantityInput.value = min;
                showAlert(`Минимальное количество: ${min}`, 'warning');
                updateQuantityButtons();
                return;
            }
            
            if (currentValue > max) {
                quantityInput.value = max;
                showAlert(`Доступно только ${max} шт. на складе`, 'warning');
                updateQuantityButtons();
                return;
            }
            
            updateQuantityButtons();
            const formData = new FormData();
            formData.append('quantity', quantityInput.value);
            // Get CSRF token from main form
            const csrfToken = document.querySelector('#cartForm input[name="csrfmiddlewaretoken"]')?.value ||
                             document.querySelector('form input[name="csrfmiddlewaretoken"]')?.value;
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken);
            }
            const itemId = form.dataset.itemId;
            const action = form.dataset.action || form.action;
            const originalValue = quantityInput.defaultValue || quantityInput.value;
            
            // Disable input and buttons during request
            quantityInput.disabled = true;
            if (decreaseBtn) decreaseBtn.disabled = true;
            if (increaseBtn) increaseBtn.disabled = true;
            
            fetch(action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.headers.get('content-type')?.includes('application/json')) {
                    window.location.reload();
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return;
                if (data.success) {
                    if (data.removed) {
                        // Item was removed, reload page
                        window.location.reload();
                    } else {
                        // Update item price
                        const itemPriceCandidates = document.querySelectorAll(`.cart-item-price[data-item-id="${itemId}"] .price-current`);
                        const itemPriceEl = Array.from(itemPriceCandidates).find(element => {
                            const cartItem = element.closest('.cart-item');
                            return cartItem && cartItem.offsetParent !== null;
                        }) || itemPriceCandidates[0];
                        const quantity = parseInt(quantityInput.value);
                        // Update all variants (desktop + mobile) of this item
                        itemPriceCandidates.forEach(el => {
                            const price = parseFloat(el.dataset.price || 0);
                            const itemTotal = price * quantity;
                            el.textContent = `${window.formatPrice(itemTotal)} ₴`;
                            el.dataset.quantity = quantity;
                        });

                        // Recalculate totals based on checked items with updated quantities
                        recalculateCartTotals();
                        
                        // Update cart count in navbar
                        const cartBadge = document.querySelector('.navbar-link-cart .cart-badge');
                        const cartLink = document.querySelector('.navbar-link-cart');
                        
                        if (data.cart_count > 0) {
                            if (cartBadge) {
                                cartBadge.textContent = data.cart_count;
                            } else if (cartLink && data.cart_count > 0) {
                                const badge = document.createElement('span');
                                badge.className = 'cart-badge';
                                badge.textContent = data.cart_count;
                                cartLink.appendChild(badge);
                            }
                        } else if (cartBadge) {
                            cartBadge.remove();
                        }
                    }
                } else {
                    // Show error and revert value
                    const errorMsg = data.error || 'Ошибка при обновлении количества';
                    showAlert(errorMsg, 'error');
                    quantityInput.value = originalValue;
                    updateQuantityButtons();
                    
                    // If error is about stock, update max attribute
                    if (errorMsg.includes('Недостаточно') || errorMsg.includes('Доступно')) {
                        const maxMatch = errorMsg.match(/Доступно:\s*(\d+)/);
                        if (maxMatch) {
                            const newMax = parseInt(maxMatch[1]);
                            quantityInput.max = newMax;
                            quantityInput.dataset.max = newMax;
                            form.dataset.maxQuantity = newMax;
                            // Ensure current value doesn't exceed max
                            if (parseInt(quantityInput.value) > newMax) {
                                quantityInput.value = newMax;
                            }
                            updateQuantityButtons();
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error updating quantity:', error);
                showAlert('Произошла ошибка при обновлении количества', 'error');
                quantityInput.value = originalValue;
            })
            .finally(() => {
                quantityInput.disabled = false;
                quantityInput.defaultValue = quantityInput.value;
                updateQuantityButtons(); // This will re-enable buttons based on current value
            });
        });
    });
    
    // Cart checkbox functionality - recalculate totals
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    if (itemCheckboxes.length > 0) {
        const cartVariantMediaQuery = window.matchMedia('(max-width: 768px)');

        function toggleCartItemVariants() {
            const enableSelector = cartVariantMediaQuery.matches ? '.cart-item-mobile' : '.cart-item-desktop';
            const disableSelector = cartVariantMediaQuery.matches ? '.cart-item-desktop' : '.cart-item-mobile';

            document.querySelectorAll(disableSelector).forEach(item => {
                item.setAttribute('aria-hidden', 'true');
                item.querySelectorAll('input, select, textarea, button').forEach(element => {
                    if (!element.disabled) {
                        element.dataset.variantDisabled = 'true';
                        element.disabled = true;
                    }
                });
            });

            document.querySelectorAll(enableSelector).forEach(item => {
                item.setAttribute('aria-hidden', 'false');
                item.querySelectorAll('input, select, textarea, button').forEach(element => {
                    if (element.dataset.variantDisabled === 'true') {
                        element.disabled = false;
                        delete element.dataset.variantDisabled;
                    }
                });
            });

            recalculateCartTotals();
        }

        toggleCartItemVariants();
        cartVariantMediaQuery.addEventListener('change', toggleCartItemVariants);

        function setupSwipeActions() {
            const swipeThreshold = 80;
            const maxSwipe = 120;
            const cartItemsMobile = document.querySelectorAll('.cart-item-mobile');

            function setItemState(item, checkbox) {
                if (!item || !checkbox) return;
                item.classList.toggle('is-disabled', !checkbox.checked);
            }

            cartItemsMobile.forEach(item => {
                const content = item.querySelector('.cart-item-mobile-content');
                const deleteBtn = item.querySelector('.swipe-delete-btn');
                const toggleBtn = item.querySelector('.swipe-toggle-btn');
                const checkbox = item.querySelector('.item-checkbox');

                let startX = 0;
                let startY = 0;
                let tracking = false;
                let lastTranslate = 0;

                function closeItem() {
                    item.classList.remove('swipe-open', 'swiping');
                    if (content) {
                        content.style.transform = 'translateX(0)';
                    }
                }

                function openLeft() {
                    item.classList.add('swipe-open');
                    item.classList.remove('swipe-open-right');
                    item.classList.remove('swiping');
                    if (content) {
                        content.style.transform = `translateX(-${maxSwipe}px)`;
                    }
                }

                function toggleSelection() {
                    if (!checkbox) return;
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                    closeItem();
                }

                if (checkbox) {
                    setItemState(item, checkbox);
                    if (toggleBtn) {
                        toggleBtn.textContent = checkbox.checked ? 'Не добавлять' : 'Добавить';
                    }
                }

                if (toggleBtn) {
                    toggleBtn.addEventListener('click', event => {
                        event.preventDefault();
                        toggleSelection();
                    });
                }

                if (deleteBtn) {
                    deleteBtn.addEventListener('click', event => {
                        event.preventDefault();
                        const itemId = item.dataset.itemId;
                        const removeUrl = item.dataset.removeUrl;
                        removeCartItemById(itemId, removeUrl);
                    });
                }

                if (checkbox) {
                    checkbox.addEventListener('change', () => {
                        setItemState(item, checkbox);
                        if (toggleBtn) {
                            toggleBtn.textContent = checkbox.checked ? 'Не добавлять' : 'Добавить';
                        }
                    });
                }

                item.addEventListener('touchstart', event => {
                    if (event.touches.length !== 1) return;
                    if (event.target.closest('input, button, a')) return;
                    const touch = event.touches[0];
                    startX = touch.clientX;
                    startY = touch.clientY;
                    tracking = true;
                });

                item.addEventListener('touchmove', event => {
                    if (!tracking || event.touches.length !== 1 || !content) return;
                    const touch = event.touches[0];
                    const deltaX = touch.clientX - startX;
                    const deltaY = touch.clientY - startY;

                    if (Math.abs(deltaX) <= Math.abs(deltaY)) return;

                    event.preventDefault();
                    item.classList.add('swiping');
                    const base = item.classList.contains('swipe-open') ? -maxSwipe : 0;
                    const nextTranslate = Math.max(-maxSwipe, Math.min(maxSwipe, base + deltaX));
                    content.style.transform = `translateX(${nextTranslate}px)`;
                    lastTranslate = nextTranslate;
                }, { passive: false });

                item.addEventListener('touchend', event => {
                    if (!tracking) return;
                    tracking = false;
                    const touch = event.changedTouches[0];
                    const deltaX = touch.clientX - startX;
                    const deltaY = touch.clientY - startY;
                    if (Math.abs(deltaX) <= Math.abs(deltaY)) {
                        item.classList.remove('swiping');
                        return;
                    }

                    if (deltaX < -swipeThreshold || lastTranslate <= -swipeThreshold) {
                        openLeft();
                    } else if (deltaX > swipeThreshold || lastTranslate >= swipeThreshold) {
                        toggleSelection();
                    } else {
                        closeItem();
                    }
                });
            });
        }

        setupSwipeActions();

        const removeButtons = document.querySelectorAll('.cart-remove-btn');
        removeButtons.forEach(button => {
            button.addEventListener('click', event => {
                event.preventDefault();
                const cartItem = button.closest('.cart-item');
                const itemId = cartItem?.dataset.itemId;
                const removeUrl = button.dataset.removeUrl || button.getAttribute('href');
                removeCartItemById(itemId, removeUrl);
            });
        });
        // payment functions (must be defined before recalculateCartTotals)

        
        function updatePaymentInfo() {
            const selectedPayment = document.querySelector('input[name="payment_method"]:checked');
            const paymentTypeEl = document.querySelector('#paymentTypeValue');
            
            if (selectedPayment && paymentTypeEl) {
                const paymentNames = {
                    'cash': 'Наличная',
                    'paid': 'Безналичная'
                };
                
                paymentTypeEl.textContent = paymentNames[selectedPayment.value] || 'Наличная';
            }
        }
        
        function recalculateCartTotals() {
            const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
            
            let totalPrice = 0;
            let totalDiscount = 0;
            
            checkedBoxes.forEach(checkbox => {
                if (checkbox.disabled) return;
                const cartItem = checkbox.closest('.cart-item');
                if (!cartItem || cartItem.offsetParent === null) return;
                
                const priceEl = cartItem.querySelector('.cart-item-price .price-current');
                if (priceEl) {
                    const price = parseFloat(priceEl.dataset.price || 0);
                    const oldPrice = parseFloat(priceEl.dataset.oldPrice || priceEl.dataset.price || 0);
                    const quantity = parseInt(priceEl.dataset.quantity || 1);

                    totalPrice += oldPrice * quantity;
                    if (oldPrice > price) {
                        totalDiscount += (oldPrice - price) * quantity;
                    }
                }
            });
            
            // Update cart summary
            const totalPriceEl = document.querySelector('.cart-total-price');
            const totalDiscountEl = document.querySelector('.cart-total-discount');
            const discountSection = totalDiscountEl ? totalDiscountEl.closest('.cart-summary-item.discount') : null;
            
            if (totalPriceEl) {
                totalPriceEl.textContent = `${window.formatPrice(totalPrice)} ₴`;
            }
            
            if (totalDiscount > 0) {
                if (totalDiscountEl) {
                    totalDiscountEl.textContent = `-${window.formatPrice(totalDiscount)} ₴`;
                }
                if (discountSection) {
                    discountSection.style.display = '';
                }
            } else {
                if (discountSection) {
                    discountSection.style.display = 'none';
                }
            }

            // Update final price (items only, delivery cost added by delivery.js)
            const finalPriceElCheck = document.querySelector('#finalPrice');
            if (finalPriceElCheck) {
                const finalValue = Math.max(0, totalPrice - totalDiscount);
                window.cartItemsFinalPrice = finalValue;
                const deliveryCost = window.cartDeliveryCost || 0;
                finalPriceElCheck.textContent = `${window.formatPrice(finalValue + deliveryCost)} ₴`;
            }
        }
        
        // Delivery and payment change handlers

        
        const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
        if (paymentRadios.length > 0) {
            paymentRadios.forEach(radio => {
                radio.addEventListener('change', updatePaymentInfo);
            });
        }

        const recipientRadios = document.querySelectorAll('input[name="recipient_type"]');
        if (recipientRadios.length > 0) {
            recipientRadios.forEach(radio => {
                radio.addEventListener('change', toggleRecipientFields);
            });
        }
        
        // Initialize delivery and payment info

        updatePaymentInfo();

        
        // Update checkbox button icon and tooltip
        function updateCheckboxIcon(checkbox) {
            const iconElement = checkbox.nextElementSibling;
            const labelElement = checkbox.closest('label.checkbox-button');
            
            if (iconElement && iconElement.classList.contains('checkbox-button-icon')) {
                iconElement.textContent = checkbox.checked ? '✓' : '0';
            }
            
            // Update tooltip
            if (labelElement) {
                labelElement.title = checkbox.checked ? 'Не добавлять' : 'Добавить';
            }
        }
        
        // Initialize checkbox icons and tooltips
        itemCheckboxes.forEach(checkbox => {
            updateCheckboxIcon(checkbox);
            checkbox.addEventListener('change', function() {
                updateCheckboxIcon(checkbox);
                recalculateCartTotals();
            });
        });
        
        // Format all initial prices in cart (if formatAllPrices didn't catch them)
        document.querySelectorAll('.cart-item-price .price-current').forEach(window.formatPriceElement);
        
        // Initial calculation
        recalculateCartTotals();
    }

    const courierForms = document.querySelectorAll('.courier-delivery-form');
    if (courierForms.length > 0) {
        function setCollapsibleStateSimple(element, isVisible, transitionMs = 280) {
            if (!element) return;
            element.setAttribute('aria-hidden', (!isVisible).toString());
            if (isVisible) {
                element.hidden = false;
                requestAnimationFrame(() => {
                    element.classList.add('is-visible');
                });
            } else {
                element.classList.remove('is-visible');
                window.setTimeout(() => {
                    element.hidden = true;
                }, transitionMs);
            }
        }

        function syncCourierForms() {
            courierForms.forEach(form => {
                const container = form.closest('form') || document;
                const selected = container.querySelector('input[name="delivery_type"]:checked');
                const isCourier = selected?.value === 'courier';
                const isNovaPost = selected?.value === 'nova-posta';
                setCollapsibleStateSimple(form, isCourier);
                form.querySelectorAll('[data-courier-required]').forEach(field => {
                    if (isCourier || isNovaPost) {
                        field.setAttribute('required', 'required');
                    } else {
                        field.removeAttribute('required');
                    }
                });
            });
        }

        document.querySelectorAll('input[name="delivery_type"]').forEach(radio => {
            radio.addEventListener('change', syncCourierForms);
        });
        syncCourierForms();
    }
});
