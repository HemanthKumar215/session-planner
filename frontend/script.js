document.addEventListener('DOMContentLoaded', () => {
    // Get references to all necessary DOM elements
    const subjectSelect = document.getElementById('subject');
    const preparationDaysInput = document.getElementById('preparationDays');
    const targetScoreInput = document.getElementById('targetScore');
    const generateScheduleBtn = document.getElementById('generateScheduleBtn');
    const resetBtn = document.getElementById('resetBtn');
    const errorMessageDiv = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const loadingSpinnerDiv = document.getElementById('loadingSpinner');
    const scheduleOutputDiv = document.getElementById('scheduleOutput');
    const scheduleList = document.getElementById('scheduleList');
    const initialMessage = document.getElementById('initialMessage');
    const currentYearSpan = document.getElementById('currentYear');

    // Set the current year in the footer dynamically
    currentYearSpan.textContent = new Date().getFullYear();

    /**
     * Toggles the enabled/disabled state of form elements and buttons.
     * @param {boolean} enabled - True to enable, false to disable.
     */
    function setFormEnabled(enabled) {
        subjectSelect.disabled = !enabled;
        preparationDaysInput.disabled = !enabled;
        targetScoreInput.disabled = !enabled;
        generateScheduleBtn.disabled = !enabled;
        resetBtn.disabled = !enabled;

        // Add/remove Tailwind opacity and cursor classes for visual feedback
        if (!enabled) {
            generateScheduleBtn.classList.add('opacity-50', 'cursor-not-allowed');
            resetBtn.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
            generateScheduleBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            resetBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    /**
     * Displays an error message on the UI.
     * @param {string} message - The error message to display.
     */
    function showErrorMessage(message) {
        errorText.textContent = message;
        errorMessageDiv.classList.remove('hidden'); // Make the error div visible
    }

    /**
     * Hides the error message from the UI.
     */
    function hideErrorMessage() {
        errorMessageDiv.classList.add('hidden'); // Hide the error div
        errorText.textContent = ''; // Clear the error text
    }

    /**
     * Shows the loading spinner and disables form interaction.
     * @param {string} message - Optional message to display under the spinner.
     */
    function showLoadingSpinner(message = 'Generating your personalized schedule...') {
        initialMessage.classList.add('hidden'); // Hide the initial message
        scheduleOutputDiv.classList.add('hidden'); // Hide any previously displayed schedule
        loadingSpinnerDiv.classList.remove('hidden'); // Show the loading spinner
        document.getElementById('loadingMessage').textContent = message; // Set loading message
        setFormEnabled(false); // Disable form elements during loading
    }

    /**
     * Hides the loading spinner and re-enables form interaction.
     */
    function hideLoadingSpinner() {
        loadingSpinnerDiv.classList.add('hidden'); // Hide the loading spinner
        setFormEnabled(true); // Re-enable form elements
    }

    /**
     * Displays the generated study schedule on the UI.
     * @param {Array<Object>} schedule - An array of schedule objects, each with 'day' and 'topics'.
     */
    function displaySchedule(schedule) {
        hideLoadingSpinner(); // Hide loading spinner
        hideErrorMessage();   // Hide any error messages
        initialMessage.classList.add('hidden'); // Hide initial message
        scheduleOutputDiv.classList.remove('hidden'); // Show the schedule output div
        scheduleList.innerHTML = ''; // Clear any previous schedule items

        if (schedule && schedule.length > 0) {
            schedule.forEach(dayPlan => {
                const listItem = document.createElement('li');
                listItem.className = 'bg-gray-800 p-4 rounded-lg border border-gray-700'; // Apply Tailwind classes
                listItem.innerHTML = `
                    <h3 class="text-lg font-semibold text-blue-400 mb-2">Day ${dayPlan.day}</h3>
                    <ul class="list-disc list-inside text-gray-300 space-y-1">
                        ${dayPlan.topics.map(topic => `<li>${topic}</li>`).join('')}
                    </ul>
                `;
                scheduleList.appendChild(listItem); // Add the day's plan to the list
            });
        } else {
            // Display a message if no schedule was generated or it's empty
            scheduleList.innerHTML = '<li class="text-gray-400 text-center">No schedule generated.</li>';
        }
    }

    /**
     * Resets the form inputs and returns the UI to its initial state.
     */
    function resetForm() {
        subjectSelect.value = 'Biology'; // Reset subject to default
        preparationDaysInput.value = ''; // Clear days input
        targetScoreInput.value = '';     // Clear score input
        hideErrorMessage();              // Hide errors
        hideLoadingSpinner();            // Hide loading spinner
        scheduleOutputDiv.classList.add('hidden'); // Hide schedule display
        initialMessage.classList.remove('hidden'); // Show initial prompt
    }

    // Event listener for the "Generate Schedule" button click
    generateScheduleBtn.addEventListener('click', async () => {
        hideErrorMessage(); // Clear any previous errors

        // Get current values from input fields
        const subject = subjectSelect.value;
        const preparationDays = parseInt(preparationDaysInput.value);
        const targetScore = parseInt(targetScoreInput.value);

        // Basic client-side validation
        if (!subject || isNaN(preparationDays) || isNaN(targetScore)) {
            showErrorMessage('Please fill in all fields.');
            return; // Stop execution if validation fails
        }
        if (preparationDays <= 0) {
            showErrorMessage('Preparation days must be a positive number.');
            return;
        }
        if (targetScore <= 0 || targetScore > 100) {
            showErrorMessage('Target score must be between 1 and 100.');
            return;
        }

        showLoadingSpinner(); // Show loading indicator

        try {
            // --- BACKEND INTEGRATION POINT ---
            // This is where you make the actual API call to your Grok AI powered backend.
            // Replace the URL with your backend's actual endpoint.
            const response = await fetch('http://localhost:5000/api/generate-schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subject,
                    preparationDays,
                    targetScore,
                    // You might include other data here if your backend requires it,
                    // such as parsed curriculum topics if it doesn't read them directly.
                }),
            });

            // Check if the network request was successful (HTTP status 200-299)
            if (!response.ok) {
                const errorData = await response.json(); // Attempt to parse error message from backend
                throw new Error(errorData.message || 'Failed to generate schedule from backend.');
            }

            const data = await response.json(); // Parse the JSON response from the backend
            displaySchedule(data.schedule); // Call function to display the received schedule

        } catch (err) {
            // Catch and handle any errors during the fetch operation or response parsing
            console.error('Error generating schedule:', err);
            hideLoadingSpinner(); // Hide loading spinner even on error
            showErrorMessage(err.message || 'An unexpected error occurred. Please try again.');
        }
    });

    // Event listener for the "Reset" button click
    resetBtn.addEventListener('click', resetForm);
});
