document.addEventListener('DOMContentLoaded', function () {
    const customSelects = document.querySelectorAll('.custom-select');

    function updateSelectedOptions(customSelect) {
        const selectedOptions = Array.from(customSelect.querySelectorAll(".option.active")).filter(
            option => option !== customSelect.querySelector('.option.all-tags')).map(function (option) {
            return {
                value: option.getAttribute("data-value"),
                text: option.textContent.trim()
            };
        });

        const selectedValues = selectedOptions.map(
            function (option) {
                return option.value;
            }
        );

        customSelect.querySelector('.tags_input').value = selectedValues.join(', ');
        let tagsHTML = "";

        if (selectedOptions.length === 0) {
            tagsHTML = '<span class="placeholder">Select the tags</span>';
        } else {
            const maxTagsToShow = 4;
            let additionalTagsCount = 0;

            selectedOptions.forEach(function (option, index) {
                if (index < maxTagsToShow) {
                    tagsHTML += '<span class="tag">' + option.text + '<span class="remove-tag" data-value="'
                        + option.value + '">&times;</span></span>';
                } else {
                    additionalTagsCount++;
                }
            });
            if (additionalTagsCount > 0) {
                tagsHTML += '<span class="tag">+' + additionalTagsCount + '</span>';
            }
        }
        customSelect.querySelector(".selected-options").innerHTML = tagsHTML;
    }

    customSelects.forEach(function (customSelect) {
        const searchInput = customSelect.querySelector('.search-tags');
        const optionsContainer = customSelect.querySelector('.options');
        const noResultMessage = customSelect.querySelector('.no-result-message');
        const options = customSelect.querySelectorAll('.option');
        const clearButton = customSelect.querySelector('.clear');



        clearButton.addEventListener('click', function () {
            searchInput.value = '';
            options.forEach(function (option) {
                option.style.display = 'block';
            });
            noResultMessage.style.display = 'none';
        });

        searchInput.addEventListener('input', function () {
            const searchTerm = searchInput.value.toLowerCase();
            options.forEach(function (option) {
                const optionText = option.textContent.trim().toLocaleLowerCase();
                const shouldShow = optionText.includes(searchTerm);
                option.style.display = shouldShow ? 'block' : 'none';
            });

            const anyOptionsMatch = Array.from(options).some(option => option.style.display === 'block');
            noResultMessage.style.display = anyOptionsMatch ? 'block' : 'none';

            if (searchTerm) {
                optionsContainer.classList.add('option-search-active');
            } else {
                optionsContainer.classList.remove('option-search-active');
            }
        });

        options.forEach(function (option) {
            option.addEventListener('click', function () {
                option.classList.toggle('active');
                updateSelectedOptions(customSelect)
            });
        });
    });

    document.addEventListener("click", function (event) {
        const removeTag = event.target.closest('.remove-tag');
        if (removeTag) {
            const customSelect = removeTag.closest('.custom-select');
            const valueToRemove = removeTag.getAttribute('data-value');
            const optionToRemove = customSelect.querySelector(".options .option[data-value='" + valueToRemove + "']");
            optionToRemove.classList.remove('active');

            const otherSelectedOptions = customSelect.querySelectorAll('.option.active:not(.all-tags)');

            updateSelectedOptions(customSelect);
        }
    });

    const selectBoxes = document.querySelectorAll('.select-box');
    selectBoxes.forEach(function (selectBox) {
        selectBox.addEventListener('click', function (event) {
            if (!event.target.closest(".tag")) {
                selectBox.parentNode.classList.toggle("open");
            }
        });
    });

    document.addEventListener('click', function (event) {
        if (!event.target.closest('.custom-select') || event.target.classList.contains('remove-tag')) {
            customSelects.forEach(function (customSelect) {
                customSelect.classList.remove('open');
            })
        }
    });

    function resetCustomSelects() {
        customSelects.forEach(function (customSelect) {
            customSelect.querySelectorAll(".option.active").forEach(function (option) {
                option.classList.remove('active');
            });
            customSelect.querySelector(".option.all-tags").classList.remove('active');
            updateSelectedOptions(customSelect);
        });
    }

    customSelects.forEach(function (customSelect) {
        updateSelectedOptions(customSelect);
    });

    const submitButton = document.querySelector(".btn-submit");
    submitButton.addEventListener("click", function () {
        let valid = true;
        customSelects.forEach(function (customSelect) {
            const selectedOptions = customSelect.querySelectorAll('.option.active');
            if (selectedOptions.length === 0) {
                const tagErrorMsg = customSelect.querySelector('.tag_error_message');
                tagErrorMsg.textContent = "This field is required";
                tagErrorMsg.style.display = 'block';
                valid = false;
            } else {
                const tagErrorMsg = customSelect.querySelector('.tag_error_message');
                tagErrorMsg.textContent = "";
                tagErrorMsg.style.display = 'none';
            }
        });

        if (valid) {
            let tags = document.querySelector(".tags_input").value;
            // alert(tags);
            resetCustomSelects();
        }
    });
});
