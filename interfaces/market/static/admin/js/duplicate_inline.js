document.addEventListener("click", function (e) {
    if (!e.target.closest(".duplicate-product-btn")) return;
    e.preventDefault();

    var btn = e.target.closest(".duplicate-product-btn");
    var sourceRow = btn.closest(".inline-related");
    var rowId = sourceRow && sourceRow.id;
    if (!rowId) return;

    var prefix = rowId.replace(/-\d+$/, "");
    var sourceIndex = parseInt(rowId.replace(prefix + "-", ""), 10);

    // Read source values before "Add another" changes the DOM
    var values = {};
    ["quantity", "price", "old_price"].forEach(function (field) {
        var el = document.getElementById("id_" + prefix + "-" + sourceIndex + "-" + field);
        values[field] = el ? el.value : "";
    });
    var isActiveEl = document.getElementById("id_" + prefix + "-" + sourceIndex + "-is_active");
    values.is_active = isActiveEl ? isActiveEl.checked : false;

    var specValues = [];
    var sourceSpecs = document.getElementById("id_" + prefix + "-" + sourceIndex + "-specifications");
    if (sourceSpecs) {
        for (var i = 0; i < sourceSpecs.options.length; i++) {
            if (sourceSpecs.options[i].selected) {
                specValues.push(sourceSpecs.options[i].value);
            }
        }
    }

    // Django fires "formset:added" on the new row element (bubbles to document)
    document.addEventListener("formset:added", function handler(event) {
        document.removeEventListener("formset:added", handler);

        var newRow = event.target;
        var newPrefix = event.detail.formsetName;
        var newIndex = parseInt(newRow.id.replace(newPrefix + "-", ""), 10);



        ["quantity", "price", "old_price"].forEach(function (field) {
            var el = document.getElementById("id_" + newPrefix + "-" + newIndex + "-" + field);
            if (el) el.value = values[field];
        });

        var newIsActive = document.getElementById("id_" + newPrefix + "-" + newIndex + "-is_active");
        if (newIsActive) newIsActive.checked = values.is_active;

        // Select2 is initialized by jazzmin after formset:added.
        // Use native dispatchEvent so all jQuery instances hear the change.
        var specsId = "id_" + newPrefix + "-" + newIndex + "-specifications";
        setTimeout(function () {
            var el = document.getElementById(specsId);
            if (!el) return;
            Array.prototype.forEach.call(el.options, function (opt) {
                opt.selected = specValues.indexOf(opt.value) !== -1;
            });
            el.dispatchEvent(new Event("change", { bubbles: true }));
        }, 100);

        newRow.scrollIntoView({ behavior: "smooth" });
    });

    // Trigger "Add another"
    var addBtn = sourceRow.closest(".inline-group").querySelector(".add-row a, a.addlink");
    if (addBtn) addBtn.click();
});
