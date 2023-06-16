/**
 * Displays the user message on the chat screen. This is the right side message.
 */
function showUserMessage(message, datetime) {
    renderMessageToScreen({
        text: message,
        time: datetime,
        message_side: 'right',
    });
}

/**
 * Displays the chatbot message on the chat screen. This is the left side message.
 */
function showBotMessage(message, datetime) {
    renderMessageToScreen({
        text: message,
        time: datetime,
        message_side: 'left',
    });
}

/**
 * Get input from user and show it on screen on button click.
 */
$('#send_button').on('click', sendMessage);
$('#msg_input').on('keydown', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    var userMessage = $('#msg_input').val().trim();

    if (userMessage !== '') {
        // Send user message to the backend
        $.ajax({
            url: '/processchat',
            type: 'GET',
            data: {
                text: userMessage,
            },
            success: function (response) {
                // Show user message
                showUserMessage(userMessage);

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



/**
 * Renders a message on the chat screen based on the given arguments.
 * This is called from the `showUserMessage` and `showBotMessage`.
 */
function renderMessageToScreen(args) {
    // local variables
    let displayDate = (args.time || getCurrentTimestamp()).toLocaleString('en-IN', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
    });
    let messagesContainer = $('.messages');

    // init element
    let message = $(`
        <li class="message ${args.message_side}">
            <div class="avatar"></div>
            <div class="text_wrapper">
                <div class="text">${args.text}</div>
                <div class="timestamp">${displayDate}</div>
            </div>
        </li>
    `);

    // add to parent
    messagesContainer.append(message);

    // animations
    setTimeout(function () {
        message.addClass('appeared');
    }, 0);
    messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}

/**
 * Returns the current datetime for the message creation.
 */
function getCurrentTimestamp() {
    return new Date();
}

/**
 * Set initial bot message to the screen for the user.
 */
$(window).on('load', function () {
    showBotMessage('Hello I am RISA your healthcare chatbot!.');
});
