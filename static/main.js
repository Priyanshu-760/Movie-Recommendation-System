document.getElementById('recommend-btn').onclick = async function() {
  const inputElement = document.getElementById('movie-input');
  const title = inputElement.value;
  
  // Check if a movie is entered
  if (!title) {
    alert('Please enter a movie name!');
    return;
  }
  
  // Show loading animation
  const loadingElement = document.getElementById('loading');
  const listElement = document.getElementById('recommendation-list');
  loadingElement.style.display = 'block';
  listElement.innerHTML = '';
  
  try {
    const response = await fetch('/recommend', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ movie_title: title }),
    });
    
    const data = await response.json();
    
    // Hide loading animation
    loadingElement.style.display = 'none';
    
    // Display recommendations
    listElement.innerHTML = '';
    
    if (data.recommendations && data.recommendations.length > 0) {
      // Check if we have an error message
      if (typeof data.recommendations[0] === 'string' && data.recommendations[0].includes("Movie not found")) {
        const li = document.createElement('li');
        li.textContent = data.recommendations[0];
        li.className = 'error-message';
        listElement.appendChild(li);
        return;
      }
      
      data.recommendations.forEach((movie, index) => {
        const li = document.createElement('li');
        li.className = 'movie-card';
        
        // Create movie card content
        let posterHtml = '';
        if (movie.poster && movie.poster !== 'N/A') {
          posterHtml = `<img src="${movie.poster}" alt="${movie.title}" class="movie-poster" onerror="this.src='https://via.placeholder.com/300x450?text=No+Image+Available'">`;
        } else {
          posterHtml = `<div class="movie-poster-placeholder"><span>No Image</span></div>`;
        }
        
        li.innerHTML = `
          ${posterHtml}
          <div class="movie-info">
            <h3 class="movie-title">${movie.title} (${movie.year})</h3>
            <div class="movie-meta">
              <span class="rating">⭐ ${movie.imdbRating}</span>
              <span class="duration">${movie.runtime}</span>
              <span class="genre">${movie.genre}</span>
            </div>
            <p class="movie-plot">${movie.plot}</p>
          </div>
        `;
        
        // Add animation delay for each item
        li.style.animationDelay = `${index * 0.1}s`;
        listElement.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'No recommendations found. Try another movie!';
      li.className = 'error-message';
      listElement.appendChild(li);
    }
  } catch (error) {
    // Hide loading animation
    loadingElement.style.display = 'none';
    
    // Show error message
    listElement.innerHTML = '';
    const li = document.createElement('li');
    li.textContent = 'Error fetching recommendations. Please try again later.';
    li.className = 'error-message';
    listElement.appendChild(li);
    console.error('Error:', error);
  }
}

// Add hover effect to recommendation items
document.addEventListener('mouseover', function(e) {
  if (e.target.tagName === 'LI' && e.target.classList.contains('movie-card')) {
    e.target.classList.add('floating');
  }
});

document.addEventListener('mouseout', function(e) {
  if (e.target.tagName === 'LI' && e.target.classList.contains('movie-card')) {
    e.target.classList.remove('floating');
  }
});

// Allow pressing Enter in the input field to trigger recommendation
document.getElementById('movie-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
    document.getElementById('recommend-btn').click();
  }
});