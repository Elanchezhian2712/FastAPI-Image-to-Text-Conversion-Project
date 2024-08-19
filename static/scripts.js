let startX, startY, endX, endY;
let selectionBox;
let isSelecting = false;
let selectedField = '';

const fieldMapping = {
    "GOVT RANK": "govt_rank",
    "APPLICATION NUMBER": "application_number",
    "NAME OF THE CANDIDATE": "name",
    "DATE OF BIRTH": "dob",
    "AGGREGATE MARK": "aggregate_mark",
    "COMMUNITY": "community",
    "GOVT COMMUNITY RANK": "govt_community_rank"
};

function startSelection(event) {
    if (event.ctrlKey) {
        if (isSelecting) return;

        const imgElement = document.getElementById('processed-image');
        if (!imgElement) return;

        const rect = imgElement.getBoundingClientRect();
        startX = event.clientX - rect.left;
        startY = event.clientY - rect.top;

        selectionBox = document.createElement('div');
        selectionBox.className = 'selectable-box';
        selectionBox.style.left = `${startX}px`;
        selectionBox.style.top = `${startY}px`;
        document.getElementById('image-container').appendChild(selectionBox);

        isSelecting = true;
        document.getElementById('cancel-button').style.display = 'inline';

        document.addEventListener('mousemove', updateSelection);
        document.addEventListener('mouseup', endSelection);
    }
}

function updateSelection(event) {
    if (!isSelecting) return;

    const imgElement = document.getElementById('processed-image');
    const rect = imgElement.getBoundingClientRect();
    endX = event.clientX - rect.left;
    endY = event.clientY - rect.top;

    selectionBox.style.width = `${Math.abs(endX - startX)}px`;
    selectionBox.style.height = `${Math.abs(endY - startY)}px`;
    selectionBox.style.left = `${Math.min(startX, endX)}px`;
    selectionBox.style.top = `${Math.min(startY, endY)}px`;
}

function endSelection(event) {
    if (!isSelecting) return;

    document.removeEventListener('mousemove', updateSelection);
    document.removeEventListener('mouseup', endSelection);

    const imgElement = document.getElementById('processed-image');
    const rect = imgElement.getBoundingClientRect();
    endX = event.clientX - rect.left;
    endY = event.clientY - rect.top;

    const x1 = Math.min(startX, endX);
    const y1 = Math.min(startY, endY);
    const x2 = Math.max(startX, endX);
    const y2 = Math.max(startY, endY);

    fetchText(x1, y1, x2, y2);

    selectionBox.remove();
    isSelecting = false;
    document.getElementById('cancel-button').style.display = 'none';
}

function cancelSelection() {
    if (isSelecting) {
        selectionBox.remove();
        document.removeEventListener('mousemove', updateSelection);
        document.removeEventListener('mouseup', endSelection);
        isSelecting = false;
        document.getElementById('cancel-button').style.display = 'none';
    }
}

function fetchText(x1, y1, x2, y2) {
    const x1Int = Math.round(x1);
    const y1Int = Math.round(y1);
    const x2Int = Math.round(x2);
    const y2Int = Math.round(y2);

    fetch(`/get_text/?x1=${x1Int}&y1=${y1Int}&x2=${x2Int}&y2=${y2Int}`)
        .then(response => response.json())
        .then(data => {
            if (data.text) {
                autoFillField(data.text);
            } else {
                alert('Error extracting text');
            }
        })
        .catch(error => alert('An error occurred: ' + error));
}
function autoFillField(extractedText) {
    if (!selectedField) {
        alert("No field selected.");
        return;
    }

    const fieldId = fieldMapping[selectedField];
    if (fieldId) {
        const inputElement = document.getElementById(fieldId);
        if (inputElement) {
            let value = extractedText.trim().toUpperCase().replace(/\|/g, '');

            if (fieldId === 'dob') {
                value = convertDateFormat(value);
            }

            inputElement.value = value;
        }
    }
}
function drawBoundingBoxes(boxes) {
    const imgElement = document.getElementById('processed-image');
    const container = document.getElementById('image-container');

    // Remove any existing bounding boxes
    const existingBoxes = document.querySelectorAll('.selectable-box');
    existingBoxes.forEach(box => box.remove());

    // Draw each bounding box
    boxes.forEach(box => {
        const { x1, y1, x2, y2 } = box;
        const boxElement = document.createElement('div');
        boxElement.className = 'selectable-box';
        boxElement.style.left = `${x1}px`;
        boxElement.style.top = `${y1}px`;
        boxElement.style.width = `${x2 - x1}px`;
        boxElement.style.height = `${y2 - y1}px`;
        container.appendChild(boxElement);

        boxElement.addEventListener('click', () => {
            // Example bounding box click handling
            fetchText(x1, y1, x2, y2);
        });
    });
}

function convertDateFormat(dateStr) {
    const parts = dateStr.split('-');
    if (parts.length === 3) {
        const day = parts[0];
        const month = parts[1];
        const year = parts[2];
        return `${year}-${month}-${day}`;
    }
    return dateStr;
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('processed-image').addEventListener('mousedown', startSelection);

    document.getElementById('field-select').addEventListener('change', (event) => {
        selectedField = event.target.value;
    });
});