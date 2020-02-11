$(document).ready(() => {
  $('#searchForm').on('submit', (e) => {
    let searchText = $('#searchText').val();
    getMovies(searchText);
    e.preventDefault();
  });

});



function getTrending() {
  axios.get('https://api.themoviedb.org/3/trending/movie/week?api_key=8bad0ff15fd3be44dc71e4e5c9107c92&language=en-US&page=1&include_adult=false')
    .then((response) => {
      console.log(response);
      let trending = response.data.results;
      let output = '';
      for (let movie in trending) {
        let poster_src = "https://image.tmdb.org/t/p/w185" + trending[movie].poster_path;

        output += `
            <div class="col-md-3">
              <div class="text-center">
                <img src="${poster_src}" alt="movie poster">
                <h5>${trending[movie].original_title}</h5>
                <p>${trending[movie].vote_average}</p>
                <a onclick="movieSelected('${trending[movie].id}')" class="btn btn-warning" href="#">Movie Details</a>
                </div>
                <hr>
            </div>
            
            `;

      }
      $('#trending').html(output);

    })


    .catch((err) => {
      console.log(err);
    });
}


function getMovies(searchText) {
  axios.get('https://api.themoviedb.org/3/search/movie?api_key=8bad0ff15fd3be44dc71e4e5c9107c92&language=en-US&page=1&include_adult=false&query=' + searchText)
    .then((response) => {
      console.log(response);
      let movies = response.data.results;
      let output = '';
      for (let movie in movies) {
        let poster_src = "https://image.tmdb.org/t/p/w185" + movies[movie].poster_path;
        if (movies[movie].poster_path != null) {
          output += `
            <div class="col-md-3">
              <hr>
              <div class="text-center">
                <img src="${poster_src}" alt="movie poster">
                <h5>${movies[movie].original_title}</h5>
                <p>${movies[movie].vote_average}</p>
                <a onclick="movieSelected('${movies[movie].id}')" class="btn btn-warning">Movie Details</a>
              </div>
              <hr>
            </div>
          `;
        } else {
          output += `
        <div class="col-md-3">
          <hr>
          <div class="text-center">
            <p> No Movie Poster Available</p>
            <h5>${movies[movie].original_title}</h5>
            <p>${movies[movie].vote_average}</p>
            <a onclick="movieSelected('${movies[movie].id}')" class="btn btn-warning">Movie Details</a>
          </div>
          <hr>
        </div>
      `;;
        }
      };

      $('#movies').html(output);
    })
    .catch((err) => {
      console.log(err);
    });
}


function movieSelected(id) {
  sessionStorage.setItem('movieId', id);
  window.location.assign('/search_results');
  return false;
}

function getMovie() {
  let movieId = sessionStorage.getItem('movieId');
  axios.get('https://api.themoviedb.org/3/movie/' + movieId + '?api_key=8bad0ff15fd3be44dc71e4e5c9107c92&language=en-US&page=1&include_adult=false')
    .then((response) => {
      console.log(response);
      let movie = response.data;
      let poster_src = "https://image.tmdb.org/t/p/w185" + movie.poster_path
      let output = `
          <div class="row">
            <div class="col-md-4">
              <img src="${poster_src}" class="thumbnail">
            </div>
            <div id="info" class="col-md-8">
              <h2>${movie.title}</h2>
              <h4 id="tagline">${movie.tagline}<h4>
              <ul class="list-group">
                <li class="list-group-item"><strong>Released:</strong> ${movie.release_date}</li>
                <li class="list-group-item"><strong>Rated:</strong> ${movie.vote_average}/10</li>
                <li class="list-group-item"><strong>Runtime:</strong> ${movie.runtime} minutes</li>
              </ul>
            </div>
          </div>
          <div class="row">
            <div>
              <h3 id="plot">Plot</h3>
              <p>${movie.overview}</p>
              <hr>
              <a href="http://imdb.com/title/${movie.imdb_id}" target="_blank" class="btn btn-warning">View IMDB</a>
              <a href="/new" class="btn btn-warning">Write a Review!<a>
              <a href="/movie_search" class="btn btn-warning">Go Back To Search</a>
            </div>
          </div>
        `;

      $('#movie').html(output);
    })
    .catch((err) => {
      console.log(err);
    });
    
  axios.get('https://api.themoviedb.org/3/movie/' + movieId + '/reviews?api_key=8bad0ff15fd3be44dc71e4e5c9107c92&language=en-US&page=1&include_adult=false')
    .then((response_reviews) => {
      console.log(response_reviews);
      let movie_reviews = response_reviews.data.results;
      let output_reviews = '';
      for (review in movie_reviews) {
        output_reviews += `
          <div class="col-md-8">
            <ul class="list-group">
              <li class="list-group-item"><strong>Author:</strong> ${movie_reviews[review].author}</li>
              <li class="list-group-item"><strong>Review:</strong> ${movie_reviews[review].content}</li>
            </ul>
          </div>
          `;
      }
      $('#reviews').html(output_reviews);

    })
    .catch((err) => {
      console.log(err);
    });
}