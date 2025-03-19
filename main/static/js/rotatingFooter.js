// Footer with typewriter effect

$(document).ready(function() {
  // Footer rotating word effect
  const footerWordElement = $('#footer-rotating-word');
  const footerContainerElement = $('#footer-rotating-word-container');
  const footerWords = [
    'WITH US.',
    'ONLINE.',
    'TODAY.',
    'ANYTIME.',
    'SOCIALLY.'
  ];

  if (footerWordElement.length && footerContainerElement.length && footerWords.length) {
    // Set minimum width to accommodate the longest word
    let longestWord = '';
    for (const word of footerWords) {
      if (word.length > longestWord.length) {
        longestWord = word;
      }
    }
    footerContainerElement.css('min-width', (longestWord.length * 12) + 'px');
    
    // Initialize with the first word already displayed
    let currentWordIndex = 0;
    let isDeleting = false;
    let currentText = 'WITH US.';
    let typingSpeed = 100;
    
    function footerTypeEffect() {
      const currentWord = footerWords[currentWordIndex];
      
      if (isDeleting) {
        // Deleting text
        currentText = currentText.substring(0, currentText.length - 1);
        typingSpeed = 80;
      } else {
        // Typing text
        currentText = currentWord.substring(0, currentText.length + 1);
        typingSpeed = 150;
      }
      
      // Update the displayed text
      footerWordElement.text(currentText);
      
      // Word cycling logic
      if (!isDeleting && currentText === currentWord) {
        // Finished typing the word, pause for 3s then start deleting
        typingSpeed = 3000;
        isDeleting = true;
      } else if (isDeleting && currentText === '') {
        isDeleting = false;
        currentWordIndex = (currentWordIndex + 1) % footerWords.length;
        typingSpeed = 500;
      }
      setTimeout(footerTypeEffect, typingSpeed);
    }
    
    setTimeout(footerTypeEffect, 3000);
  }
});