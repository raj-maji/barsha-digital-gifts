// Barsha Digital Gift - Interactive JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Image & Text Preview for Customizable Gifts
    const customImageInput = document.getElementById('custom_image_input');
    const previewImage = document.getElementById('preview_custom_image');
    const previewPlaceholder = document.getElementById('preview_placeholder');
    const customTextInput = document.getElementById('custom_text_input');
    const previewText = document.getElementById('preview_custom_text');

    if (customImageInput && previewImage) {
        customImageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    previewImage.classList.remove('d-none');
                    if (previewPlaceholder) {
                        previewPlaceholder.classList.add('d-none');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (customTextInput && previewText) {
        customTextInput.addEventListener('input', function() {
            const val = this.value.trim();
            if (val.length > 0) {
                previewText.textContent = `"${val}"`;
                previewText.classList.remove('d-none');
            } else {
                previewText.textContent = '';
                previewText.classList.add('d-none');
            }
        });
    }

    // 2. Copy UPI ID helper
    const copyUpiBtn = document.getElementById('btn_copy_upi');
    if (copyUpiBtn) {
        copyUpiBtn.addEventListener('click', function() {
            const upiId = this.getAttribute('data-upi');
            navigator.clipboard.writeText(upiId).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check2"></i> Copied!';
                this.classList.remove('btn-outline-primary');
                this.classList.add('btn-success');
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-primary');
                }, 2500);
            });
        });
    }

    // 3. Auto dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
