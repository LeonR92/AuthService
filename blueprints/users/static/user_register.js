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