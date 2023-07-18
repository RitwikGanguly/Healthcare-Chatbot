function showUserMessage(message, datetime) {
    renderMessageToScreen({
        text: message,
        time: datetime,
        message_side: 'right',
    });
}

function showBotMessage(message, datetime) {
    renderMessageToScreen({
        text: message,
        time: datetime,
        message_side: 'left',
    });
}

function sendMessage() {
    var userMessage = $('#msg_input').val().trim();

    if (userMessage !== '') {
        // Show user message
        showUserMessage(userMessage);

        // Send user message to the backend
        $.ajax({
            url: '/processchat',
            type: 'GET',
            data: {
                text: userMessage,
            },
            success: function (response) {
                // Show bot message
                setTimeout(function () {
                    showBotMessage(response);
                }, 300);
            },
            error: function (error) {
                console.log('Error:', error);
            }
        });
    }

    // Reset input
    $('#msg_input').val('');
}

$('#send_button').on('click', sendMessage);
$('#msg_input').on('keydown', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendMessage();
    }
});

function renderMessageToScreen(args) {
    let displayDate = (args.time || getCurrentTimestamp()).toLocaleString('en-IN', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
    });
    let messagesContainer = $('.messages');

    let message = $(`
        <li class="message ${args.message_side}">
            <div class="avatar"></div>
            <div class="text_wrapper">
                <div class="text">${args.text}</div>
                <div class="timestamp">${displayDate}</div>
            </div>
        </li>
    `);

    messagesContainer.append(message);

    setTimeout(function () {
        message.addClass('appeared');
    }, 0);
    messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}

function getCurrentTimestamp() {
    return new Date();
}

$(window).on('load', function () {
    showBotMessage('Hello I am RISA, your healthcare chatbot!, Now I am With Version 2.0.2');
});
