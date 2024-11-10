document.addEventListener('DOMContentLoaded', function () {
    // Setup file preview
    document.getElementById('file-upload').addEventListener('change', previewFile);

    // Show popup with farming tips if not dismissed
    if (!sessionStorage.getItem('popupDismissed')) {
        setTimeout(showPopup, 2000); // Show popup after 2 seconds
    }

    // Attach close event to close button for popup
    document.getElementById('popup-close').addEventListener('click', closePopup);

    // Fetch weather data immediately on page load
    getWeather();

    // Attach event listener to the "Get Weather" button
    document.getElementById('get-weather-btn').addEventListener('click', function () {
        const city = document.getElementById('city-input').value.trim();
        getWeather(city); // Fetch weather based on the city input
    });
});

// Get weather data based on the user's location or a city name

// Function to fetch real-time weather data
async function getWeatherData(city) {
    const apiKey = '0d8f4c834b1bec7b7a29afcd0cf01ab5'; // Replace with your OpenWeatherMap API key
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;
  
    try {
      const response = await fetch(url);
      const data = await response.json();
  
      if (data.cod !== 200) {
        // Display error message if city not found or API error
        document.querySelector("#weather .error").innerText = "Error fetching weather data.";
        return;
      }
  
      // Extracting relevant weather data
      const temperature = data.main.temp;
      const description = data.weather[0].description;
      const humidity = data.main.humidity;
      const windSpeed = data.wind.speed;
      const weatherIcon = `http://openweathermap.org/img/w/${data.weather[0].icon}.png`; // Get icon for weather
  
      // Updating the weather section dynamically
      document.querySelector("#weather h2").innerText = `Weather in ${city}`;
      document.querySelector(".weather-info .temperature").innerText = `${temperature}°C`;
      document.querySelector(".weather-info .description").innerText = description;
      document.querySelector(".weather-info .weather-icon").setAttribute("src", weatherIcon);
      document.querySelector(".additional-info p:nth-child(1)").innerText = `Humidity: ${humidity}%`;
      document.querySelector(".additional-info p:nth-child(2)").innerText = `Wind Speed: ${windSpeed} m/s`;
  
      // Hide error message if everything is okay
      document.querySelector("#weather .error").style.display = "none";
    } catch (error) {
      console.error("Error fetching weather data:", error);
      document.querySelector("#weather .error").innerText = "Unable to fetch weather data. Please try again later.";
    }
  }
  
  // Call the function to fetch weather data on page load
  document.addEventListener("DOMContentLoaded", () => {
    const city = "Kolhapur"; // You can change the city dynamically
    getWeatherData(city);
  });
  
// Fetch weather data by city name

// Function to display weather data in the UI
// Function to fetch weather data by city or default location


// List of farming tips messages (now 122 messages)
const messages = [
    "Did you know? Regular soil testing can help optimize crop yield and quality.",
    "Irrigating sugarcane fields at regular intervals is essential for healthy crop growth!",
    "Planting cover crops can improve soil fertility and reduce weeds naturally.",
    // Add more tips as needed
];

// Function to show the popup with a random message
function showPopup() {
    // Get a random message from the messages array
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];

    // Set the popup text
    document.getElementById('popup-text').textContent = randomMessage;

    // Display the popup
    document.getElementById('popup').style.display = 'flex';
}

// Function to close the popup
function closePopup() {
    document.getElementById('popup').style.display = 'none';  // Hide popup
}

// Preview file before uploading
function previewFile() {
    const file = document.getElementById('crop-image').files[0]; // Corrected ID
    const preview = document.getElementById('file-preview');

    const reader = new FileReader();
    reader.onloadend = function () {
        preview.src = reader.result;
        preview.style.display = 'block';
    };

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = 'none';
    }
}
