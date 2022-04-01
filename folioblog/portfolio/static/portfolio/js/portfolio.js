(() => {
    window.addEventListener('DOMContentLoaded', event => {
        let emailElem = document.body.querySelector('.email-mailto');
        let email = atob(emailElem.getAttribute('data-email'));
        emailElem.href = 'mailto:' + email;

        let phoneElem = document.body.querySelector('.phone-number');
        let phone = atob(phoneElem.getAttribute('data-phone'));
        phoneElem.href = 'tel:' + phone;
    });
})();
