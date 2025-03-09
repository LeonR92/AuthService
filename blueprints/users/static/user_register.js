document.addEventListener('DOMContentLoaded', async function() {
    const countrySelect = document.getElementById('country');
    
    const loadingOption = document.createElement('option');
    loadingOption.textContent = 'Loading countries...';
    countrySelect.appendChild(loadingOption);
    
    try {
      // Async fetch
      const response = await fetch('https://restcountries.com/v3.1/all?fields=name,cca2');
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const countries = await response.json();
      
      const fragment = document.createDocumentFragment();
      
      // Sort countries
      countries.sort((a, b) => a.name.common.localeCompare(b.name.common));
      
      countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.cca2;
        option.textContent = country.name.common;
        fragment.appendChild(option);
      });
      
      countrySelect.removeChild(loadingOption);
      
      countrySelect.appendChild(fragment);
      
    } catch (error) {
      console.error('Error fetching countries:', error);
      
      countrySelect.removeChild(loadingOption);
      
      const fragment = document.createDocumentFragment();
      
      // Fallback countries if API not working
      const fallbackCountries = [
        { code: 'US', name: 'United States' },
        { code: 'GB', name: 'United Kingdom' },
        { code: 'CA', name: 'Canada' },
        { code: 'AU', name: 'Australia' },
        { code: 'DE', name: 'Germany' },
        { code: 'FR', name: 'France' },
        { code: 'JP', name: 'Japan' },
        { code: 'CN', name: 'China' },
        { code: 'IN', name: 'India' },
        { code: 'BR', name: 'Brazil' },
      ];
      
      fallbackCountries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.code;
        option.textContent = country.name;
        fragment.appendChild(option);
      });
      
      countrySelect.appendChild(fragment);
    }
  });



  // DOB controller
  document.addEventListener('DOMContentLoaded', function() {
    // Get date input element
    const dateInput = document.getElementById('dob');
    
    // Set max attribute to today's date
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('max', today);
    
    // Add validation when date changes
    dateInput.addEventListener('change', function() {
      const selectedDate = new Date(this.value);
      const currentDate = new Date();
      
      // Check if date is in the future
      if(selectedDate > currentDate) {
        alert('Please select a date in the past for your birthday.');
        this.value = ''; 
      }
    });
  });



  // Toggle

document.addEventListener('DOMContentLoaded', function() {
  // Get elements
  const toggleButton = document.getElementById('mfa_toggle');
  const toggleSlider = toggleButton.querySelector('span');
  const statusText = document.getElementById('is_mfa');
  const hiddenInput = document.getElementById('mfa_enabled');
  
  // Initial state
  let isEnabled = false;
  statusText.textContent = "MFA not activated";
  
  // Toggle function
  toggleButton.addEventListener('click', function() {
    // Toggle state
    isEnabled = !isEnabled;
    
    // Update hidden input value - this is what the backend will receive
    hiddenInput.value = isEnabled.toString();
    
    // Update aria attribute
    toggleButton.setAttribute('aria-checked', isEnabled);
    
    // Update button background
    if (isEnabled) {
      toggleButton.classList.remove('bg-gray-200');
      toggleButton.classList.add('bg-indigo-600');
    } else {
      toggleButton.classList.remove('bg-indigo-600');
      toggleButton.classList.add('bg-gray-200');
    }
    
    // Update slider position
    if (isEnabled) {
      toggleSlider.classList.remove('translate-x-0');
      toggleSlider.classList.add('translate-x-5');
    } else {
      toggleSlider.classList.remove('translate-x-5');
      toggleSlider.classList.add('translate-x-0');
    }
    
    // Update status text
    statusText.textContent = isEnabled ? "MFA activated" : "MFA not activated";
  });
});
