// login.js
$(document).ready(function(){
    $('#login-form').submit(function(event){
        event.preventDefault();
        var formData = {
            id_number: $('#id_number').val()
        };
        $.ajax({
            type: 'POST',
            url: '/login',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response){
                $('#message').text(response.message);
                // Redirect or perform any other action after successful login
            },
            error: function(xhr, status, error){
                var errorMessage = xhr.responseJSON.error;
                $('#message').text(errorMessage);
            }
        });
    });
});
