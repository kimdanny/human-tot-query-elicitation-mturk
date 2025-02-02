xml_template_20_urls = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
  <HTMLContent><![CDATA[
<script src="https://assets.crowd.aws/crowd-html-elements.js"></script>

<style>
    .hidden {
        display: none;
    }

    .flex-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .image-wrapper {
        flex: 1;
    }

    .text-button-wrapper {
        flex: 1;
        padding: 20px;
    }

    .progress-container {
        margin-bottom: 10px;
    }

    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 5px;
    }

    .progress {
        height: 100%;
        border-radius: 5px;
        transition: width 0.4s ease;
    }

    .progress-red {
        background-color: red;
    }

    .progress-orange {
        background-color: orange;
    }

    .progress-green {
        background-color: green;
    }

    .character-counter {
        text-align: right;
        margin-top: -20px;
    }

    .status-message {
        color: #d9534f; /* default to red */
        margin-bottom: 5px;
    }

    .tot-query-input-wrapper {
        width: 80%; /* Adjust this value to match the text area size */
        margin: auto;
    }

    #tot-query-input {
        margin-bottom: 20px; /* Increased gap between the text area and buttons */
    }

    textarea { font-size: 18px; }
    crowd-input { font-size: 18px; }
</style>

<!-- Phase 0: Instructions -->
<div id="instruction-container">
    <div class="instructions-content">
        <p>
            <b>If this is your first time doing this HIT, please read the instructions below carefully. Thank you.</b><br><br>

            You will be shown a series of images of popular movies.
            They might correspond to a poster of the movie or a scene from the movie.
            While you go through each image, see if you recognize the movie.
            If you recognize the movie, we will ask if you remember the name.
            If you recognize the movie, but <b>DO NOT</b> remember the name, then you are in a <b>"Tip of the Tongue" (ToT)</b> state.
            This is like in being a situation where you can’t remember a word but it’s on the "tip of your tongue"!<br><br>

            On the internet, there are online communities (for example, on Reddit) that help people resolve their ToT information needs with the help of other community members.
            On such communities, someone will start a new thread by posting a ToT information request.
            Information requests are about a paragraph long.
            In response to a ToT request, community members will then take turns guessing the correct answer.
            The thread ends when the original poster confirms that someone guessed the correct answer.<br><br>

            If you are in a ToT state, we want you to pretend that you are posting a ToT information request on one of these online communities.
            Your information request should be about a paragraph long.
            Please include any information that comes natural to you.
            Also, please include <b>ANY and ALL</b> information that you think might help other community members determine the correct answer.
            Typical ToT information requests include memories, things you know and don’t know, comparisons, and mentions of uncertainty, to name just a few.<br><br>

            After submitting your ToT information request, you will be shown a Wikipedia page that might correspond to the correct answer.
            You will be asked to confirm if the Wikipedia page corresponds to the correct answer.
            We hope that the Wikipedia page corresponds to the correct answer.
            However, it is completely okay to indicate that it does not.
        </p>
        <div class="example">
            <p>To illustrate, consider the following movie scene:</p>
            <p><img src="https://tot-mturk-instruction-images.s3.amazonaws.com/titanic.jpg" width="200" height="116"/></p>
            <p><strong>This is an example of a GOOD ToT information request:</strong></p>
            <p>
                <em>
                I saw this movie when I was young, but I guess it was released before I was born, so probably before 2000.
                The storyline goes like this. A male character and a female character were on a cruise ship,
                but the ship hits a big iceberg and starts to sink.
                I think they both die (not sure of this), but I remember a specific scene where the male character was holding on to a wood plank
                in a cold water with very pale blue face. I don't know the ending,
                but I heard this was based on a true story.
                There's also a very famous movie theme song. Genre can be romance, disaster and/or historic.
                What's the name of this movie?
                </em>
            </p>
        </div>
        <div class="example">
            <p><strong>This is an example of a BAD ToT information request:</strong></p>
            <p>
                <em>The cruise ship sinked in ocean and there were two main characters.</em>
            </p>
        </div>
    </div>
    <button type="button" id="start-task-button">Start Task</button>
</div>

<!-- Phase 1: Recognize -->
<div id="image-container" class="hidden">
    <img id="hit-image" width="800" height="600">
    <p>Do you recognize this movie?</p>
    <button type="button" id="yes-button">Yes</button>
    <button type="button" id="no-button">No</button>
</div>

<!-- Phase 2: Movie Name -->
<div id="movie-name-container" class="hidden">
    <p>Do you remember the name of the movie?</p>
    <button type="button" id="remember-yes-button">Yes</button>
    <button type="button" id="remember-no-button">No</button>
</div>

<div id="movie-name-input-container" class="hidden">
    <p><strong>Please write the name of the movie:</strong></p>
    <crowd-input id="movie-name-input" name="movie-name" label="Type the movie name here..."></crowd-input>
    <button type="button" id="go-back-from-movie-name-input">Go Back</button>
    <button type="button" id="submit-movie-name-button">Submit Movie Name</button>
</div>

<!-- Phase 3: ToT Query -->
<div id="tot-query-container" class="hidden">
    <p><strong>Please input your ToT information request:</strong></p>
    <div class="tot-query-input-wrapper">
        <div class="progress-container">
            <div class="progress-bar">
                <div id="progress" class="progress progress-red" style="width: 0%;"></div>
            </div>
            <div class="character-counter" id="character-counter">0 characters</div>
        </div>
        <div class="status-message" id="status-message">Please input text in the text box below.</div>
        <textarea id="tot-query-input" name="tot-query" rows="6" cols="80" placeholder="Type your ToT information request here..."></textarea>
    </div>
    <button type="button" id="go-back-from-tot-query-input">Go Back</button>
    <button type="button" id="submit-tot-query-button">Submit ToT information request</button>
</div>

<!-- Phase 4: Confirm -->
<div id="confirm-container" class="hidden">
    <iframe id="wiki-frame" style="width: 90%; height: 600px;"></iframe>
    <p>Does this Wikipedia page describe the movie you recalled?</p>
    <button type="button" id="confirm-yes-button">Yes</button>
    <button type="button" id="confirm-no-button">No</button>
</div>

<!-- Ending Page -->
<div id="ending-container" class="hidden">
    <p><strong>You reach the end of this task. You either finished the task or running out of all the images. Now you may submit the form. Thanks!</strong></p>
    <crowd-form>
        <input type="hidden" id="mturk-data" name="mturk_data">
        <!-- Amazon Mturk submit button will be automatically included -->
    </crowd-form>
</div>

<script>
    var imageObjects = [
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'}
    ];
    var currentIndex = 0;
    var timestamps = {};
    var userResponses = {};

    var totQueryInput = document.getElementById('tot-query-input');
    var progress = document.getElementById('progress');
    var characterCounter = document.getElementById('character-counter');
    var statusMessage = document.getElementById('status-message');

    function showImage(index) {
        var imageElement = document.getElementById('hit-image');
        var imageId = imageObjects[index].id;
        imageElement.src = imageObjects[index].url;

        // Initialize user response for this image if it doesn't exist
        if (!userResponses[imageId]) {
            userResponses[imageId] = {};
        }

        // Retrieve and set the stored movie name, if available
        var movieNameInput = document.getElementById('movie-name-input');
        movieNameInput.value = userResponses[imageId]['movieName'] || '';
    }

    function nextImage() {
        if (currentIndex < imageObjects.length - 1) {
            currentIndex++;
            showImage(currentIndex);
        // if running out of all the images, go to the ending page
        } else {
            // End of image list reached, transition to Ending Page
            prepareDataForSubmission();
            togglePhaseVisibility('image-container', 'ending-container');
        }
    }

    function togglePhaseVisibility(currentPhase, nextPhase) {
        document.getElementById(currentPhase).classList.add('hidden');
        document.getElementById(nextPhase).classList.remove('hidden');
    }

    function storeTimestamp(phase) {
        timestamps[phase] = new Date().toISOString();
    }

    function storeResponse(phase, response) {
        var imageId = imageObjects[currentIndex].id;
        userResponses[imageId][phase] = response;
    }

    function validateInput(inputId, minLength) {
        var input = document.getElementById(inputId).value.trim();
        return input.length >= minLength;
    }

    function prepareDataForSubmission() {
        var mturkDataInput = document.getElementById('mturk-data');
        mturkDataInput.value = JSON.stringify({ userResponses, timestamps });
    }

    function updateCharacterCount() {
        var charCount = totQueryInput.value.length;
        characterCounter.textContent = charCount + ' characters';
        var progressWidth = (charCount / 400 * 100); // Full width corresponds to 400 characters

        if (charCount === 0) {
            progress.className = 'progress progress-red';
            progress.style.width = '0%'; // No progress for 0 characters
            statusMessage.textContent = 'Please input text in the text box below.';
            statusMessage.style.color = 'red';
        } else if (charCount < 200) {
            progress.className = 'progress progress-red';
            progress.style.width = progressWidth + '%';
            statusMessage.textContent = 'The text is too short!';
            statusMessage.style.color = 'red';
        } else if (charCount >= 200 && charCount < 300) {
            progress.className = 'progress progress-orange';
            progress.style.width = progressWidth + '%';
            statusMessage.textContent = 'Can you be more specific?';
            statusMessage.style.color = 'orange';
        } else {
            progress.className = 'progress progress-green';
            progress.style.width = Math.min(progressWidth, 100) + '%'; // Cap at 100% width
            statusMessage.textContent = '';
            statusMessage.style.color = 'green';
        }
    }

    // Event listeners and transition logic

    // Event Listener for 'Start Task' Button (Phase 0 to Phase 1)
    document.getElementById('start-task-button').addEventListener('click', function() {
        togglePhaseVisibility('instruction-container', 'image-container');
        storeTimestamp('phase_0_timestamp');
    });

    // Event Listeners for 'Yes' and 'No' Buttons in Phase 1
    document.getElementById('yes-button').addEventListener('click', function() {
        storeResponse('Phase_1_(recognize)', 'Yes');
        storeTimestamp('phase_1_timestamp');
        togglePhaseVisibility('image-container', 'movie-name-container');
    });
    document.getElementById('no-button').addEventListener('click', function() {
        storeResponse('Phase_1_(recognize)', 'No');
        storeTimestamp('phase_1_timestamp');
        nextImage();
    });

    // Event Listeners for 'Yes' and 'No' Buttons in Phase 2
    document.getElementById('remember-yes-button').addEventListener('click', function() {
        storeResponse('Phase_2_(object_name)', 'Yes');
        togglePhaseVisibility('movie-name-container', 'movie-name-input-container');
    });
    document.getElementById('remember-no-button').addEventListener('click', function() {
        storeResponse('Phase_2_(object_name)', 'N/A');
        storeTimestamp('phase_2_timestamp');
        togglePhaseVisibility('movie-name-container', 'tot-query-container');
    });

    // Event Listener for 'Submit Movie Name' Button in Phase 2
    document.getElementById('submit-movie-name-button').addEventListener('click', function() {
        if (validateInput('movie-name-input', 3)) {
            var movieName = document.getElementById('movie-name-input').value;
            storeResponse('Phase_2_(object_name)', movieName);
            storeTimestamp('phase_2_timestamp');
            togglePhaseVisibility('movie-name-input-container', 'image-container');
            nextImage(); // Load the next image if any
        } else {
            // Display an alert if the input is too short
            alert('Please enter a movie name. The input must be longer than 3 character.');
        }
    });

    // Event Listener for 'tot-query-container' in Phase 3
    totQueryInput.addEventListener('input', updateCharacterCount);

    // Event Listener for 'Submit ToT Query' Button in Phase 3
    document.getElementById('submit-tot-query-button').addEventListener('click', function() {
        if (validateInput('tot-query-input', 200)) {
            storeResponse('Phase_3_(ToT_query)', document.getElementById('tot-query-input').value);
            storeTimestamp('phase_3_timestamp');
            togglePhaseVisibility('tot-query-container', 'confirm-container');
            document.getElementById('wiki-frame').src = imageObjects[currentIndex].wiki_page;
        } else {
            // Display an alert if the input is too short
            alert('Please enter a detailed ToT information request. The input must be longer than 200 characters.');
        }
    });

    // Event Listeners for 'Yes' and 'No' Buttons in Phase 4
    document.getElementById('confirm-yes-button').addEventListener('click', function() {
        storeResponse('Phase_4_(confirm)', 'Yes');
        storeTimestamp('phase_4_timestamp');
        prepareDataForSubmission();
        togglePhaseVisibility('confirm-container', 'ending-container');
    });

    document.getElementById('confirm-no-button').addEventListener('click', function() {
        storeResponse('Phase_4_(confirm)', 'No');
        storeTimestamp('phase_4_timestamp');
        prepareDataForSubmission();
        togglePhaseVisibility('confirm-container', 'ending-container');
    });

    // Event Listener for 'Go Back' Button in movie-name-input-container to movie-name-container
    document.getElementById('go-back-from-movie-name-input').addEventListener('click', function() {
        togglePhaseVisibility('movie-name-input-container', 'movie-name-container');
    });
    // Event Listener for 'Go Back' Button in tot-query-container to movie-name-container
    document.getElementById('go-back-from-tot-query-input').addEventListener('click', function() {
        togglePhaseVisibility('tot-query-container', 'movie-name-container');
    });

    window.onload = function() {
        showImage(currentIndex);
        // initial timestamp, timestamps for each phase are recorded at the end of them
        storeTimestamp('intial_timestamp');
    };
</script>

  ]]>
  </HTMLContent>
  <FrameHeight>750</FrameHeight>
</HTMLQuestion>
"""

xml_template_50_urls = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
  <HTMLContent><![CDATA[
<script src="https://assets.crowd.aws/crowd-html-elements.js"></script>

<style>
    .hidden {
        display: none;
    }

    .flex-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .image-wrapper {
        flex: 1;
    }

    .text-button-wrapper {
        flex: 1;
        padding: 20px;
    }

    .progress-container {
        margin-bottom: 10px;
    }

    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 5px;
    }

    .progress {
        height: 100%;
        border-radius: 5px;
        transition: width 0.4s ease;
    }

    .progress-red {
        background-color: red;
    }

    .progress-orange {
        background-color: orange;
    }

    .progress-green {
        background-color: green;
    }

    .character-counter {
        text-align: right;
        margin-top: -20px;
    }

    .status-message {
        color: #d9534f; /* default to red */
        margin-bottom: 5px;
    }

    .tot-query-input-wrapper {
        width: 80%; /* Adjust this value to match the text area size */
        margin: auto;
    }

    #tot-query-input {
        margin-bottom: 20px; /* Increased gap between the text area and buttons */
    }

    textarea { font-size: 18px; }
    crowd-input { font-size: 18px; }
</style>

<!-- Phase 0: Instructions -->
<div id="instruction-container">
    <div class="instructions-content">
        <p>
            <b>If this is your first time doing this HIT, please read the instructions below carefully. Thank you.</b><br><br>

            You will be shown a series of images of public figures.
            They can be actors, actresses, artists, politicians, painters, writers, sports players, etc.
            While you go through each image, see if you recognize the person.
            If you recognize the person, we will ask if you remember their name.
            If you recognize the person, but <b>DO NOT</b> remember their name, then you are in a <b>"Tip of the Tongue" (ToT)</b> state.
            This is like in being a situation where you can’t remember a word but it’s on the “tip of your tongue”!<br><br>

            On the internet, there are online communities (for example, on Reddit) that help people resolve their ToT information needs with the help of other community members.
            On such communities, someone will start a new thread by posting a ToT information request.
            Information requests are about a paragraph long.
            In response to a ToT request, community members will then take turns guessing the correct answer.
            The thread ends when the original poster confirms that someone guessed the correct answer.<br><br>

            If you are in a ToT state, we want you to pretend that you are posting a ToT information request on one of these online communities.
            Your information request should be about a paragraph long.
            Please include any information that comes natural to you.
            Also, please include <b>ANY and ALL</b> information that you think might help other community members determine the correct answer.
            Typical ToT information requests include memories, things you know and don’t know, comparisons, and mentions of uncertainty, to name just a few.<br><br>

            After submitting your ToT information request, you will be shown a Wikipedia page that might correspond to the correct answer.
            You will be asked to confirm if the Wikipedia page corresponds to the correct answer.
            We hope that the Wikipedia page corresponds to the correct answer.
            However, it is completely okay to indicate that it does not.
        </p>
        <div class="example">
            <p>To illustrate, consider the following movie scene:</p>
            <p><img src="https://tot-mturk-instruction-images.s3.amazonaws.com/titanic.jpg" width="200" height="116"/></p>
            <p><strong>This is an example of a GOOD ToT information request:</strong></p>
            <p>
                <em>
                I saw this movie when I was young, but I guess it was released before I was born, so probably before 2000.
                The storyline goes like this. A male character and a female character were on a cruise ship,
                but the ship hits a big iceberg and starts to sink.
                I think they both die (not sure of this), but I remember a specific scene where the male character was holding on to a wood plank
                in a cold water with very pale blue face. I don't know the ending,
                but I heard this was based on a true story.
                There's also a very famous movie theme song. Genre can be romance, disaster and/or historic.
                What's the name of this movie?
                </em>
            </p>
        </div>
        <div class="example">
            <p><strong>This is an example of a BAD ToT information request:</strong></p>
            <p>
                <em>The cruise ship sinked in ocean and there were two main characters.</em>
            </p>
        </div>
    </div>
    <button type="button" id="start-task-button">Start Task</button>
</div>

<!-- Phase 1: Recognize -->
<div id="image-container" class="hidden">
    <img id="hit-image" width="800" height="600">
    <p>Do you recognize this movie?</p>
    <button type="button" id="yes-button">Yes</button>
    <button type="button" id="no-button">No</button>
</div>

<!-- Phase 2: Movie Name -->
<div id="movie-name-container" class="hidden">
    <p>Do you remember the name of the movie?</p>
    <button type="button" id="remember-yes-button">Yes</button>
    <button type="button" id="remember-no-button">No</button>
</div>

<div id="movie-name-input-container" class="hidden">
    <p><strong>Please input your ToT information request:</strong></p>
    <crowd-input id="movie-name-input" name="movie-name" label="Type the movie name here..."></crowd-input>
    <button type="button" id="go-back-from-movie-name-input">Go Back</button>
    <button type="button" id="submit-movie-name-button">Submit Movie Name</button>
</div>

<!-- Phase 3: ToT Query -->
<div id="tot-query-container" class="hidden">
    <p><strong>Please input your ToT information request:</strong></p>
    <div class="tot-query-input-wrapper">
        <div class="progress-container">
            <div class="progress-bar">
                <div id="progress" class="progress progress-red" style="width: 0%;"></div>
            </div>
            <div class="character-counter" id="character-counter">0 characters</div>
        </div>
        <div class="status-message" id="status-message">Please input text in the text box below.</div>
        <textarea id="tot-query-input" name="tot-query" rows="6" cols="80" placeholder="Type your ToT information request here..."></textarea>
    </div>
    <button type="button" id="go-back-from-tot-query-input">Go Back</button>
    <button type="button" id="submit-tot-query-button">Submit ToT information request</button>
</div>

<!-- Phase 4: Confirm -->
<div id="confirm-container" class="hidden">
    <iframe id="wiki-frame" style="width: 90%; height: 600px;"></iframe>
    <p>Does this Wikipedia page describe the movie you recalled?</p>
    <button type="button" id="confirm-yes-button">Yes</button>
    <button type="button" id="confirm-no-button">No</button>
</div>

<!-- Ending Page -->
<div id="ending-container" class="hidden">
    <p><strong>You reach the end of this task. You either finished the task or running out of all the images. Now you may submit the form. Thanks!</strong></p>
    <crowd-form>
        <input type="hidden" id="mturk-data" name="mturk_data">
        <!-- Amazon Mturk submit button will be automatically included -->
    </crowd-form>
</div>

<script>
    var imageObjects = [
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'},
        { url: '{{S3_URL}}', id: '{{IMAGE_ID}}', wiki_page: '{{WIKI_URL}}'}
    ];
    var currentIndex = 0;
    var timestamps = {};
    var userResponses = {};

    var totQueryInput = document.getElementById('tot-query-input');
    var progress = document.getElementById('progress');
    var characterCounter = document.getElementById('character-counter');
    var statusMessage = document.getElementById('status-message');

    function showImage(index) {
        var imageElement = document.getElementById('hit-image');
        var imageId = imageObjects[index].id;
        imageElement.src = imageObjects[index].url;

        // Initialize user response for this image if it doesn't exist
        if (!userResponses[imageId]) {
            userResponses[imageId] = {};
        }

        // Retrieve and set the stored movie name, if available
        var movieNameInput = document.getElementById('movie-name-input');
        movieNameInput.value = userResponses[imageId]['movieName'] || '';
    }

    function nextImage() {
        if (currentIndex < imageObjects.length - 1) {
            currentIndex++;
            showImage(currentIndex);
        // if running out of all the images, go to the ending page
        } else {
            // End of image list reached, transition to Ending Page
            prepareDataForSubmission();
            togglePhaseVisibility('image-container', 'ending-container');
        }
    }

    function togglePhaseVisibility(currentPhase, nextPhase) {
        document.getElementById(currentPhase).classList.add('hidden');
        document.getElementById(nextPhase).classList.remove('hidden');
    }

    function storeTimestamp(phase) {
        timestamps[phase] = new Date().toISOString();
    }

    function storeResponse(phase, response) {
        var imageId = imageObjects[currentIndex].id;
        userResponses[imageId][phase] = response;
    }

    function validateInput(inputId, minLength) {
        var input = document.getElementById(inputId).value.trim();
        return input.length >= minLength;
    }

    function prepareDataForSubmission() {
        var mturkDataInput = document.getElementById('mturk-data');
        mturkDataInput.value = JSON.stringify({ userResponses, timestamps });
    }

    function updateCharacterCount() {
        var charCount = totQueryInput.value.length;
        characterCounter.textContent = charCount + ' characters';
        var progressWidth = (charCount / 400 * 100); // Full width corresponds to 400 characters

        if (charCount === 0) {
            progress.className = 'progress progress-red';
            progress.style.width = '0%'; // No progress for 0 characters
            statusMessage.textContent = 'Please input text in the text box below.';
            statusMessage.style.color = 'red';
        } else if (charCount < 200) {
            progress.className = 'progress progress-red';
            progress.style.width = progressWidth + '%';
            statusMessage.textContent = 'The text is too short!';
            statusMessage.style.color = 'red';
        } else if (charCount >= 200 && charCount < 300) {
            progress.className = 'progress progress-orange';
            progress.style.width = progressWidth + '%';
            statusMessage.textContent = 'Can you be more specific?';
            statusMessage.style.color = 'orange';
        } else {
            progress.className = 'progress progress-green';
            progress.style.width = Math.min(progressWidth, 100) + '%'; // Cap at 100% width
            statusMessage.textContent = '';
            statusMessage.style.color = 'green';
        }
    }

    // Event listeners and transition logic

    // Event Listener for 'Start Task' Button (Phase 0 to Phase 1)
    document.getElementById('start-task-button').addEventListener('click', function() {
        togglePhaseVisibility('instruction-container', 'image-container');
        storeTimestamp('phase_0_timestamp');
    });

    // Event Listeners for 'Yes' and 'No' Buttons in Phase 1
    document.getElementById('yes-button').addEventListener('click', function() {
        storeResponse('Phase_1_(recognize)', 'Yes');
        storeTimestamp('phase_1_timestamp');
        togglePhaseVisibility('image-container', 'movie-name-container');
    });
    document.getElementById('no-button').addEventListener('click', function() {
        storeResponse('Phase_1_(recognize)', 'No');
        storeTimestamp('phase_1_timestamp');
        nextImage();
    });

    // Event Listeners for 'Yes' and 'No' Buttons in Phase 2
    document.getElementById('remember-yes-button').addEventListener('click', function() {
        storeResponse('Phase_2_(object_name)', 'Yes');
        togglePhaseVisibility('movie-name-container', 'movie-name-input-container');
    });
    document.getElementById('remember-no-button').addEventListener('click', function() {
        storeResponse('Phase_2_(object_name)', 'N/A');
        storeTimestamp('phase_2_timestamp');
        togglePhaseVisibility('movie-name-container', 'tot-query-container');
    });

    // Event Listener for 'Submit Movie Name' Button in Phase 2
    document.getElementById('submit-movie-name-button').addEventListener('click', function() {
        if (validateInput('movie-name-input', 3)) {
            var movieName = document.getElementById('movie-name-input').value;
            storeResponse('Phase_2_(object_name)', movieName);
            storeTimestamp('phase_2_timestamp');
            togglePhaseVisibility('movie-name-input-container', 'image-container');
            nextImage(); // Load the next image if any
        } else {
            // Display an alert if the input is too short
            alert('Please enter a movie name. The input must be longer than 3 character.');
        }
    });

    // Event Listener for 'tot-query-container' in Phase 3
    totQueryInput.addEventListener('input', updateCharacterCount);

    // Event Listener for 'Submit ToT Query' Button in Phase 3
    document.getElementById('submit-tot-query-button').addEventListener('click', function() {
        if (validateInput('tot-query-input', 200)) {
            storeResponse('Phase_3_(ToT_query)', document.getElementById('tot-query-input').value);
            storeTimestamp('phase_3_timestamp');
            togglePhaseVisibility('tot-query-container', 'confirm-container');
            document.getElementById('wiki-frame').src = imageObjects[currentIndex].wiki_page;
        } else {
            // Display an alert if the input is too short
            alert('Please enter a detailed ToT information request. The input must be longer than 200 characters.');
        }
    });

    // Event Listeners for 'Yes' and 'No' Buttons in Phase 4
    document.getElementById('confirm-yes-button').addEventListener('click', function() {
        storeResponse('Phase_4_(confirm)', 'Yes');
        storeTimestamp('phase_4_timestamp');
        prepareDataForSubmission();
        togglePhaseVisibility('confirm-container', 'ending-container');
    });

    document.getElementById('confirm-no-button').addEventListener('click', function() {
        storeResponse('Phase_4_(confirm)', 'No');
        storeTimestamp('phase_4_timestamp');
        prepareDataForSubmission();
        togglePhaseVisibility('confirm-container', 'ending-container');
    });

    // Event Listener for 'Go Back' Button in movie-name-input-container to movie-name-container
    document.getElementById('go-back-from-movie-name-input').addEventListener('click', function() {
        togglePhaseVisibility('movie-name-input-container', 'movie-name-container');
    });
    // Event Listener for 'Go Back' Button in tot-query-container to movie-name-container
    document.getElementById('go-back-from-tot-query-input').addEventListener('click', function() {
        togglePhaseVisibility('tot-query-container', 'movie-name-container');
    });

    window.onload = function() {
        showImage(currentIndex);
        // initial timestamp, timestamps for each phase are recorded at the end of them
        storeTimestamp('intial_timestamp');
    };
</script>

  ]]>
  </HTMLContent>
  <FrameHeight>750</FrameHeight>
</HTMLQuestion>"""
