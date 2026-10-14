var socket = io();

socket.on('connect', function () {
    var statusBadge = document.getElementById('status-badge');
    statusBadge.classList.remove('bg-danger');
    statusBadge.classList.add('bg-success');
    statusBadge.innerText = 'Connected';
});

socket.on('disconnect', function () {
    var statusBadge = document.getElementById('status-badge');
    statusBadge.classList.remove('bg-success');
    statusBadge.classList.add('bg-danger');
    statusBadge.innerText = 'Disconnected';
});

socket.on('sensor_data', function (data) {
    if ('infrared_data' in data) {
        var ir01 = document.getElementById('ir01');
        var ir02 = document.getElementById('ir02');
        var ir03 = document.getElementById('ir03');

        ir01.style.backgroundColor = data.infrared_data[0] ? 'green' : 'red';
        ir02.style.backgroundColor = data.infrared_data[1] ? 'green' : 'red';
        ir03.style.backgroundColor = data.infrared_data[2] ? 'green' : 'red';
    }

    if ('distance' in data) {
        var distanceBadge = document.getElementById('distance-badge');
        distanceBadge.innerText = data.distance + 'cm';
    }
});

document.addEventListener('keydown', function (event) {
    var key = event.key.toLowerCase();
    if (['w', 'a', 's', 'd', 'i', 'j', 'k', 'l'].includes(key)) {
        event.preventDefault();
        socket.emit('key_press', { 'key': key });
    }
});

document.addEventListener('keyup', function (event) {
    var key = event.key.toLowerCase();
    if (['w', 'a', 's', 'd', 'i', 'j', 'k', 'l'].includes(key)) {
        event.preventDefault();
        socket.emit('key_release', { 'key': key });
    }
});

const keyMappings = {
    'forward': 'W',
    'backward': 'S',
    'left': 'A',
    'right': 'D',
    'arm_up': 'I',
    'arm_down': 'K',
    'arm_left': 'J',
    'arm_right': 'L'
};

function emitAction(action) {
    socket.emit('action', { 'action': action });
}

function addButtonEventListeners(button, action, stopAction) {
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    if (!isTouchDevice) button.innerHTML = keyMappings[action];
    let isPressed = false;

    const startEvent = isTouchDevice ? 'touchstart' : 'mousedown';
    const endEvents = isTouchDevice ? ['touchend', 'touchcancel'] : ['mouseup', 'mouseleave'];

    button.addEventListener(startEvent, function (event) {
        if (!isTouchDevice) event.preventDefault();
        if (!isPressed) {
            isPressed = true;
            emitAction(action);
        }
    });

    endEvents.forEach(eventType => {
        button.addEventListener(eventType, function (event) {
            if (!isTouchDevice) event.preventDefault();
            if (isPressed) {
                isPressed = false;
                emitAction(stopAction);
            }
        });
    });

    button.addEventListener('contextmenu', function (event) {
        event.preventDefault();
    }, false);
}

const movementActions = ['forward', 'backward', 'left', 'right'];
movementActions.forEach(function (action) {
    var button = document.getElementById(action);
    if (button) {
        addButtonEventListeners(button, action, 'stop');
    }
});

const armActions = ['arm_up', 'arm_down', 'arm_left', 'arm_right'];
armActions.forEach(function (action) {
    var button = document.getElementById(action);
    if (button) {
        addButtonEventListeners(button, action, 'stop_arm');
    }
});


var armMenuButton = document.getElementById('arm_menu');
if (armMenuButton) {
    armMenuButton.addEventListener('click', function (event) {
        var actionModal = document.getElementById('actionModal');
        if (actionModal.style.display === 'block') {
            actionModal.style.display = 'none';
        } else {
            actionModal.style.display = 'block';
        }
    });
}

document.addEventListener('keydown', function (event) {
    if (event.key.toLowerCase() === 'm') {
        var actionModal = document.getElementById('actionModal');
        if (actionModal.style.display === 'block') {
            actionModal.style.display = 'none';
        } else {
            actionModal.style.display = 'block';
        }
    }
});

window.addEventListener('click', function (event) {
    var actionModal = document.getElementById('actionModal');
    if (event.target !== actionModal && !actionModal.contains(event.target) && event.target !== armMenuButton) {
        actionModal.style.display = 'none';
    }
});

document.querySelectorAll('li.action-item').forEach(function (item) {
    item.addEventListener('click', function (event) {
        var action = event.target.getAttribute('data-action');
        emitAction(action);
        var actionModal = document.getElementById('actionModal');
        actionModal.style.display = 'none';
    });
});

document.addEventListener('keydown', function (event) {
    const actionMap = {
        '1': 'light_up_leds',
        '2': 'reset_servos'
    };
    const action = actionMap[event.key];
    if (action) {
        emitAction(action);
        document.getElementById('actionModal').style.display = 'none';
    }
});

// A suspended tab or disconnected client must stop movement.
setInterval(function () {
    if (socket.connected && document.visibilityState === 'visible') socket.emit('heartbeat');
}, 200);
function stopMovement() {
    socket.emit('action', {action: 'stop'});
    socket.emit('action', {action: 'stop_arm'});
}
window.addEventListener('blur', stopMovement);
document.addEventListener('visibilitychange', function () {
    if (document.visibilityState !== 'visible') stopMovement();
});
