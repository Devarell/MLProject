document.addEventListener('DOMContentLoaded', () => {
    const predictionForm = document.getElementById('predictionForm');
    const predictionResultDiv = document.getElementById('predictionResult');

    if (predictionForm) {
        predictionForm.addEventListener('submit', (event) => {
           

            // Clear previous results and styles
            predictionResultDiv.textContent = '';
            predictionResultDiv.className = 'prediction-result'; // Reset class

            // --- 1. Get Form Data ---
            const formData = new FormData(predictionForm);
            const data = {};

            // Extract standard input values
            formData.forEach((value, key) => {
                // Handle checkboxes - collect all selected values for the same name
                if (predictionForm.elements[key]?.type === 'checkbox') {
                    if (!data[key]) {
                        data[key] = []; // Initialize array if first checkbox with this name
                    }
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            });

            // Log the data to the console for debugging
            console.log('Form Data Submitted: ', data);

            // --- 2. Basic Validation (Optional but Recommended) ---
            let isValid = true;
            let errorMessage = '';

            // Example: Check if required fields are filled (HTML5 'required' handles most cases)
            if (!data.educationLevel || !data.classSemester || !data.previousGrade || !data.subjectName || !data.attendanceRate || !data.assignmentRate || !data.studyHours || !data.materialDifficulty) {
                 isValid = false;
                 errorMessage = 'Harap isi semua kolom yang wajib diisi.';
            }
            // Example: Check numeric ranges (HTML5 min/max helps, but JS can double-check)
            const grade = parseFloat(data.previousGrade);
            if (isNaN(grade) || grade < 0 || grade > 100) {
                isValid = false;
                errorMessage = 'Nilai Rata-rata Sebelumnya harus antara 0 dan 100.';
            }
            // Add more specific validation rules as needed...


            // --- 3. Simulate Prediction ---
            if (isValid) {
                // Show a loading/processing message (optional)
                predictionResultDiv.textContent = 'Memproses prediksi...';
                predictionResultDiv.className = 'prediction-result'; // Neutral style while processing

                // **Replace this section with your actual prediction logic**
                // This could involve:
                // - Sending 'data' to a backend API using fetch()
                // - Running a client-side prediction model (if applicable)

                // **Simulated Delay and Result:**
                setTimeout(() => {
                    // Simulate a successful prediction result (e.g., a predicted grade)
                    // This is just a placeholder calculation
                    let predictedGrade = (parseFloat(data.previousGrade) * 0.6) +
                                         (parseFloat(data.attendanceRate) * 0.1) +
                                         (parseFloat(data.assignmentRate) * 0.15) +
                                         (parseFloat(data.studyHours) * 0.5);

                    // Add points based on difficulty (easier = higher potential baseline)
                    if(data.materialDifficulty === 'mudah') predictedGrade += 5;
                    if(data.materialDifficulty === 'sulit') predictedGrade -= 3;
                    if(data.materialDifficulty === 'sangat_sulit') predictedGrade -= 6;

                     // Add points for study methods (example)
                    if (data.studyMethod?.includes('mandiri')) predictedGrade += 1;
                    if (data.studyMethod?.includes('tutor')) predictedGrade += 3;
                    if (data.studyMethod?.includes('online')) predictedGrade += 1.5;


                    // Cap the grade at 100 and ensure it's not below 0
                    predictedGrade = Math.min(100, Math.max(0, predictedGrade));

                    // Display the result
                    predictionResultDiv.textContent = `Prediksi Nilai Anda: ${predictedGrade.toFixed(2)}`;
                    predictionResultDiv.classList.add('success'); // Add success styling

                }, 1500); // Simulate network delay (1.5 seconds)

            } else {
                // Display validation error
                predictionResultDiv.textContent = `Error: ${errorMessage}`;
                predictionResultDiv.classList.add('error'); // Add error styling
            }
        });
    }

    // Optional: Add event listener for reset button if custom behavior is needed
    // const resetButton = predictionForm.querySelector('button[type="reset"]');
    // if (resetButton) {
    //     resetButton.addEventListener('click', () => {
    //         // Clear any result messages when form is reset
    //         predictionResultDiv.textContent = '';
    //         predictionResultDiv.className = 'prediction-result';
    //     });
    // }
});