export function handleContactForm() {
  const form = document.getElementById('contact-form');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    try {
      // Simulate form submission
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show success message
      alert('Thank you for your message! We will get back to you soon.');
      form.reset();
    } catch (error) {
      alert('Sorry, there was an error sending your message. Please try again.');
    }
  });
}