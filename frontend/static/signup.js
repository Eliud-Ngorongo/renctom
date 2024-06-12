// signup.js
$(document).ready(function(){
    $('#signup-form').submit(function(event){
        event.preventDefault();
        var formData = {
            name: $('#name').val(),
            id_number: $('#id_number').val(),
            email: $('#email').val(),
            house_number: $('#house_number').val(),
            phone_number: $('#phone_number').val()
        };
        $.ajax({
            type: 'POST',
            url: '/register',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response){
                $('#message').text(response.message);
            },
            error: function(xhr, status, error){
                var errorMessage = xhr.responseJSON.error;
                $('#message').text(errorMessage);
            }
        });
    });
});
