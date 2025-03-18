// Logo animation script

$(document).ready(function() {
  function initLogoAnimation() {
    const logoElements = $('.logo-svg');
    
    if (logoElements.length) {
      logoElements.each(function() {
        const $logoImg = $(this);
        
        // Create SVG wrapper
        const svgContent = `
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" class="logo-svg-container">
            <!-- Inverted Black Triangle -->
            <path d="M75 75 L225 75 L150 225 Z" fill="black"/>
            
            <!-- White Squares Grid -->
            <rect x="125" y="100" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 0s infinite, pulse 2s ease-in-out 0s infinite;"/>
            <rect x="145" y="100" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 0.2s infinite, pulse 2s ease-in-out 0.2s infinite;"/>
            <rect x="165" y="100" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 0.4s infinite, pulse 2s ease-in-out 0.4s infinite;"/>
            <rect x="125" y="120" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 0.6s infinite, pulse 2s ease-in-out 0.6s infinite;"/>
            <rect x="145" y="120" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 0.8s infinite, pulse 2s ease-in-out 0.8s infinite;"/>
            <rect x="165" y="120" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 1s infinite, pulse 2s ease-in-out 1s infinite;"/>
            <rect x="145" y="140" width="12" height="12" fill="white" class="logo-square" style="animation: float 3s ease-in-out 1.2s infinite, pulse 2s ease-in-out 1.2s infinite;"/>
          </svg>
        `;
        
        // Preserve original classes and styles
        const originalClasses = $logoImg.attr('class');
        const originalStyles = $logoImg.attr('style');
        
        const $container = $('<div></div>').html(svgContent);
        const $svgElement = $container.find('svg');
        
        // Apply original classes and styles to new SVG
        if (originalClasses) $svgElement.addClass(originalClasses.replace('logo-svg', ''));
        if (originalStyles) $svgElement.attr('style', originalStyles);
        
        $svgElement.addClass('logo-svg');
        $logoImg.replaceWith($svgElement);
      });
    }
  }
  
  initLogoAnimation();
});