document.addEventListener('DOMContentLoaded', function() {

        function setCollapsibleState(element, isVisible, transitionMs = 280) {
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

        function setupDeliveryDatePicker() {
            const displayInput = document.getElementById('deliveryDateDisplay');
            const hiddenInput = document.getElementById('deliveryDate');
            const picker = document.getElementById('deliveryDatePicker');
            const daysContainer = document.getElementById('deliveryDateDays');
            const titleEl = document.getElementById('deliveryDateTitle');
            const prevBtn = document.getElementById('deliveryDatePrev');
            const nextBtn = document.getElementById('deliveryDateNext');
            const trigger = document.getElementById('deliveryDateTrigger');

            if (!displayInput || !hiddenInput || !picker || !daysContainer || !titleEl || !prevBtn || !nextBtn || !trigger) {
                return;
            }

            const monthNames = [
                'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
            ];

            const today = new Date();
            today.setHours(0, 0, 0, 0);

            let viewYear = today.getFullYear();
            let viewMonth = today.getMonth();
            let selectedDate = null;

            function formatDisplay(date) {
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                return `${day}.${month}.${year}`;
            }

            function formatValue(date) {
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                return `${year}-${month}-${day}`;
            }

            function renderCalendar() {
                daysContainer.innerHTML = '';
                titleEl.textContent = `${monthNames[viewMonth]} ${viewYear}`;

                const firstDay = new Date(viewYear, viewMonth, 1);
                const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
                const startIndex = (firstDay.getDay() + 6) % 7;

                for (let i = 0; i < startIndex; i += 1) {
                    const filler = document.createElement('span');
                    filler.className = 'date-picker-day is-empty';
                    daysContainer.appendChild(filler);
                }

                for (let day = 1; day <= daysInMonth; day += 1) {
                    const date = new Date(viewYear, viewMonth, day);
                    date.setHours(0, 0, 0, 0);
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'date-picker-day';
                    button.textContent = day;

                    if (date < today) {
                        button.classList.add('is-disabled');
                        button.disabled = true;
                    }

                    if (selectedDate && date.getTime() === selectedDate.getTime()) {
                        button.classList.add('is-selected');
                    }

                    button.addEventListener('click', () => {
                        selectedDate = date;
                        hiddenInput.value = formatValue(date);
                        displayInput.value = formatDisplay(date);
                        picker.hidden = true;
                        picker.classList.remove('is-visible');
                        renderCalendar();
                    });

                    daysContainer.appendChild(button);
                }
            }

            function togglePicker(forceOpen = null) {
                const shouldOpen = forceOpen !== null ? forceOpen : picker.hidden;
                if (shouldOpen) {
                    picker.hidden = false;
                    requestAnimationFrame(() => {
                        picker.classList.add('is-visible');
                    });
                } else {
                    picker.classList.remove('is-visible');
                    window.setTimeout(() => {
                        picker.hidden = true;
                    }, 200);
                }
            }

            trigger.addEventListener('click', (event) => {
                event.preventDefault();
                togglePicker();
            });

            displayInput.addEventListener('click', () => togglePicker(true));

            prevBtn.addEventListener('click', () => {
                viewMonth -= 1;
                if (viewMonth < 0) {
                    viewMonth = 11;
                    viewYear -= 1;
                }
                renderCalendar();
            });

            nextBtn.addEventListener('click', () => {
                viewMonth += 1;
                if (viewMonth > 11) {
                    viewMonth = 0;
                    viewYear += 1;
                }
                renderCalendar();
            });

            document.addEventListener('click', (event) => {
                if (!picker.contains(event.target) && !displayInput.contains(event.target) && !trigger.contains(event.target)) {
                    togglePicker(false);
                }
            });

            if (hiddenInput.value) {
                const parts = hiddenInput.value.split('-');
                if (parts.length === 3) {
                    const parsed = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
                    if (!Number.isNaN(parsed.getTime())) {
                        selectedDate = parsed;
                        viewYear = parsed.getFullYear();
                        viewMonth = parsed.getMonth();
                        displayInput.value = formatDisplay(parsed);
                    }
                }
            }

            renderCalendar();
        }


        function toggleRecipientFields() {
            const otherFields = document.getElementById('recipientOtherFields');
            if (!otherFields) return;

            const selectedRecipient = document.querySelector('input[name="recipient_type"]:checked');
            const isOther = selectedRecipient?.value === 'other';

            setCollapsibleState(otherFields, isOther);
            otherFields.querySelectorAll('[data-recipient-required]').forEach(field => {
                if (isOther) {
                    field.setAttribute('required', 'required');
                } else {
                    field.removeAttribute('required');
                }
            });
        }

        function toggleCourierDeliveryForm() {
            const courierForms = document.querySelectorAll('.courier-delivery-form');
            if (courierForms.length === 0) return;

            courierForms.forEach(courierForm => {
                const container = courierForm.closest('form') || document;
                const selectedDelivery = container.querySelector('input[name="delivery_type"]:checked');
                const isCourier = selectedDelivery?.value === 'courier';

                setCollapsibleState(courierForm, isCourier);

                courierForm.querySelectorAll('[data-courier-required]').forEach(field => {
                    if (isCourier) {
                        field.setAttribute('required', 'required');
                    } else {
                        field.removeAttribute('required');
                    }
                });
            });
        }

        function toggleNovaPostaDeliveryForm() {
            const courierForms = document.querySelectorAll('.nova-posta-delivery-form');
            if (courierForms.length === 0) return;

            courierForms.forEach(courierForm => {
                const container = courierForm.closest('form') || document;
                const selectedDelivery = container.querySelector('input[name="delivery_type"]:checked');
                const isNovaPosta = selectedDelivery?.value === 'nova_posta';

                setCollapsibleState(courierForm, isNovaPosta);

                courierForm.querySelectorAll('[data-courier-required]').forEach(field => {
                    if (isNovaPosta) {
                        field.setAttribute('required', 'required');
                    } else {
                        field.removeAttribute('required');
                    }
                });
            });
        }

        function updateDeliveryInfo() {
            const selectedDelivery = document.querySelector('input[name="delivery_type"]:checked');
            const deliveryTypeEl = document.querySelector('#deliveryTypeValue');

            if (selectedDelivery && deliveryTypeEl) {
                const deliveryPrices = {
                    'pickup': { name: 'Самовывоз' },
                    'courier': { name: 'Курьер' },
                    'nova_posta': { name: 'Nova Posta' }
                };

                const delivery = deliveryPrices[selectedDelivery.value] || deliveryPrices['pickup'];
                deliveryTypeEl.textContent = delivery.name;
                }


            toggleCourierDeliveryForm();
            toggleNovaPostaDeliveryForm();
            toggleRecipientFields();
        }


        const deliveryRadios = document.querySelectorAll('input[name="delivery_type"]');
        if (deliveryRadios.length > 0) {
            deliveryRadios.forEach(radio => {
                radio.addEventListener('change', updateDeliveryInfo);
            });
        }

        const recipientRadios = document.querySelectorAll('input[name="recipient_type"]');
        if (recipientRadios.length > 0) {
            recipientRadios.forEach(radio => {
                radio.addEventListener('change', toggleRecipientFields);
            });
        }

        updateDeliveryInfo();
        toggleRecipientFields();
        setupDeliveryDatePicker();

});