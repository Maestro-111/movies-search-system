function createTopicVisualization(containerId) {

    const container = document.getElementById(containerId);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");

    svg.setAttribute("viewBox", "0 0 800 600");

    svg.style.width = "100%";
    svg.style.height = "100%";
    svg.style.maxWidth = "800px";

    container.appendChild(svg);

    let topics = [
        { id: 1, name: "Action", importance: 0.8 },
        { id: 2, name: "Drama", importance: 0.6 },
        { id: 3, name: "Comedy", importance: 0.4 },
        { id: 4, name: "Romance", importance: 0.3 },
        { id: 5, name: "Thriller", importance: 0.7 }
    ];

    function calculatePositions() {
        const centerX = 400;
        const centerY = 300;
        const radius = 200;

        return topics.map((topic, index) => {
            const angle = (index / topics.length) * 2 * Math.PI;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            return { ...topic, x, y };
        });
    }

    function getCircleSize(importance) {
        const minSize = 40;
        const maxSize = 100;
        return minSize + (maxSize - minSize) * importance;
    }

    let draggedElement = null;
    let offset = { x: 0, y: 0 };

    function handleDragStart(event, group) {

        draggedElement = group;

        const transform = group.getAttribute("transform");
        const translate = transform.match(/translate\(([^,]+),([^)]+)\)/);
        const currentX = parseFloat(translate[1]);
        const currentY = parseFloat(translate[2]);

        const svg = group.ownerSVGElement;
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

        offset.x = currentX - svgP.x;
        offset.y = currentY - svgP.y;
    }

    function handleDrag(event) {
        if (!draggedElement) return;

        event.preventDefault();

        const svg = draggedElement.ownerSVGElement;
        const pt = svg.createSVGPoint();
        pt.x = event.clientX;
        pt.y = event.clientY;
        const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

        draggedElement.setAttribute(
            "transform",
            `translate(${svgP.x + offset.x},${svgP.y + offset.y})`
        );
    }

    function handleDragEnd() {
        draggedElement = null;
    }

    function renderTopic(topic, position) {

        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        group.setAttribute("transform", `translate(${position.x},${position.y})`);

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("r", getCircleSize(topic.importance) / 2);
        circle.style.fill = "#BFDBFE";
        circle.style.stroke = "#3B82F6";
        circle.style.strokeWidth = "2";
        circle.style.opacity = "0.8";
        circle.style.cursor = "grab"; // Change cursor to indicate draggable

        // Add drag handlers
        group.addEventListener("mousedown", (e) => handleDragStart(e, group));
        svg.addEventListener("mousemove", handleDrag);
        svg.addEventListener("mouseup", handleDragEnd);
        svg.addEventListener("mouseleave", handleDragEnd);

        circle.addEventListener("mouseenter", () => {
            circle.style.opacity = "1";
            showTopicDetails(topic);
        });
        circle.addEventListener("mouseleave", () => {
            circle.style.opacity = "0.8";
        });

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.textContent = topic.name;
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("dy", ".3em");
        text.style.fill = "#374151";
        text.style.fontSize = "14px";
        text.style.fontWeight = "500";
        text.style.pointerEvents = "none"; // Prevent text from interfering with drag

        group.appendChild(circle);
        group.appendChild(text);
        return group;
    }


    calculatePositions().forEach(topic => {
        const group = renderTopic(topic, {x: topic.x, y: topic.y});
        svg.appendChild(group);
    });

     return {
        updateTopics: function(newTopics) {
            svg.innerHTML = "";
            topics = newTopics;
            const updatedPositions = calculatePositions();
            updatedPositions.forEach(topic => {
                const group = renderTopic(topic, {x: topic.x, y: topic.y});
                svg.appendChild(group);
            });
        }
    };
}


function showTopicDetails(topic) {
    const detailsDiv = document.getElementById('topic-details');
    detailsDiv.innerHTML = `
               <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px;">
                   <h3 style="margin: 0 0 10px 0;">${topic.name}</h3>
                   <p>Importance: ${(topic.importance * 100).toFixed(1)}%</p>
                </div>
            `;
}


function updateTopicStats(topics) {

    const statsDiv = document.getElementById('topic-stats');
    const sortedTopics = [...topics].sort((a, b) => b.importance - a.importance);

    let statsHTML = '<div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px;">';

    sortedTopics.forEach(topic => {
        statsHTML += `
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <span>${topic.name}</span>
                    <span>${(topic.importance * 100).toFixed(1)}%</span>
                </div>
                <div style="background-color: #e9ecef; height: 10px; border-radius: 5px; margin-top: 5px;">
                    <div style="background-color: #3B82F6; width: ${topic.importance * 100}%; height: 100%; border-radius: 5px;"></div>
                </div>
            </div>
        `;
    });

    statsHTML += '</div>';
    statsDiv.innerHTML = statsHTML;
}

document.addEventListener('DOMContentLoaded', function() {

    const visualization = createTopicVisualization('topic-container');

    const topicContainer = document.getElementById('topic-container');
    const playlistId = topicContainer.dataset.playlistId;

    console.log("Here I am");

    fetch(`/playlist/get_user_playlist_topics/${playlistId}/`)
        .then(response => response.json())
        .then(data => {
            visualization.updateTopics(data.topics);
            updateTopicStats(data.topics);  // Add this line
        })
        .catch(error => {
            console.error('Error fetching topics:', error);
        });

});