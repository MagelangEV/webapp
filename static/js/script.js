// Cart functionality
let cartItems = [];

function updateCartCount(count) {
  const cartCount = document.getElementById('cart-count');
  cartCount.textContent = count;
  if (count > 0) {
    cartCount.classList.remove('hidden');
  } else {
    cartCount.classList.add('hidden');
  }
}

function addToCart(productId) {
  // In a real app, this would call your backend
  const product = {
    id: productId,
    name: `Product ${productId}`,
    price: Math.floor(Math.random() * 100) + 10,
    image_url: `https://picsum.photos/200/300?random=${productId}`
  };

  const existingItem = cartItems.find(item => item.id === productId);
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cartItems.push({
      ...product,
      quantity: 1
    });
  }

  updateCartCount(cartItems.reduce((sum, item) => sum + item.quantity, 0));

  Swal.fire({
    position: 'top-end',
    icon: 'success',
    title: 'Added to cart',
    showConfirmButton: false,
    timer: 1500,
    toast: true,
  });
}

function removeFromCart(productId) {
  cartItems = cartItems.filter(item => item.id !== productId);
  updateCartCount(cartItems.reduce((sum, item) => sum + item.quantity, 0));
  refreshCartModal();
}

function clearCart() {
  cartItems = [];
  updateCartCount(0);
  refreshCartModal();
}

function refreshCartModal() {
  const cartItemsContainer = document.getElementById('cart-items');
  const cartTotal = document.getElementById('cart-total');

  if (cartItems.length === 0) {
    cartItemsContainer.innerHTML = '<p class="text-center text-gray-500 py-8">Your cart is empty</p>';
    cartTotal.textContent = '$0.00';
    return;
  }

  let html = '';
  let total = 0;

  cartItems.forEach(item => {
    const itemTotal = item.price * item.quantity;
    total += itemTotal;

    html += `
      <div class="flex items-center py-4 border-b border-gray-200" id="cart-item-${item.id}">
        <img src="${item.image_url}" alt="${item.name}" class="w-16 h-16 object-cover rounded">
        <div class="ml-4 flex-grow">
          <h4 class="font-semibold text-indigo-700">${item.name}</h4>
          <p class="text-indigo-600">$${item.price.toFixed(2)} x ${item.quantity}</p>
        </div>
        <div class="ml-4 flex items-center">
          <p class="font-semibold mr-4">$${itemTotal.toFixed(2)}</p>
          <button onclick="removeFromCart(${item.id})" class="text-red-500 hover:text-red-700">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    `;
  });

  cartItemsContainer.innerHTML = html;
  cartTotal.textContent = `$${total.toFixed(2)}`;
}

function showCartModal() {
  refreshCartModal();
  document.getElementById('cart-modal').classList.remove('hidden');
}

function hideCartModal() {
  document.getElementById('cart-modal').classList.add('hidden');
}

// Checkout functionality
function processCheckout() {
  showCheckoutForm();
}

function showCheckoutForm() {
  const formHtml = `
    <div id="checkout-form-modal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-2xl font-bold text-indigo-700">Shipping Information</h3>
            <button onclick="hideCheckoutForm()" class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-times text-2xl"></i>
            </button>
          </div>

          <form id="shippingForm" onsubmit="submitShippingForm(event)">
            <div class="space-y-4 mb-6">
              <div>
                <label for="full_name" class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input type="text" id="full_name" name="full_name" required
                  class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </div>

              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input type="tel" id="phone" name="phone" required
                  class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </div>

              <div>
                <label for="address" class="block text-sm font-medium text-gray-700 mb-1">Full Address</label>
                <textarea id="address" name="address" rows="3" required
                  class="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
              </div>
            </div>

            <button type="submit" class="w-full bg-indigo-600 text-white rounded-full py-3 font-semibold hover:bg-indigo-700 transition">
              COMPLETE ORDER
            </button>
          </form>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', formHtml);
}

function hideCheckoutForm() {
  const modal = document.getElementById('checkout-form-modal');
  if (modal) modal.remove();
}

function submitShippingForm(event) {
  event.preventDefault();
  const form = event.target;
  const formData = {
    full_name: form.full_name.value,
    phone: form.phone.value,
    address: form.address.value
  };

  // Show loading
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> PROCESSING...';
  submitBtn.disabled = true;

  // Simulate API call
  setTimeout(() => {
    const orderId = 'ORD-' + Math.floor(Math.random() * 1000000);
    showReceiptModal(orderId, formData);
    hideCheckoutForm();
    hideCartModal();
    cartItems = [];
    updateCartCount(0);

    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
  }, 1500);
}

function showReceiptModal(orderId, shippingData) {
  const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  let itemsHtml = '';
  cartItems.forEach(item => {
    itemsHtml += `
      <div class="flex justify-between py-2 border-b border-gray-200">
        <div>
          <p class="font-medium">${item.name} x ${item.quantity}</p>
          <p class="text-sm text-gray-500">$${item.price.toFixed(2)} each</p>
        </div>
        <p class="font-medium">$${(item.price * item.quantity).toFixed(2)}</p>
      </div>
    `;
  });

  const addressHtml = `
    <div class="mb-6 bg-indigo-50 p-4 rounded-lg">
      <h4 class="font-semibold text-indigo-700 mb-2">Shipping To:</h4>
      <p>${shippingData.full_name}</p>
      <p>${shippingData.phone}</p>
      <p class="whitespace-pre-line">${shippingData.address}</p>
    </div>
  `;

  const receiptHtml = `
    <div class="bg-white rounded-lg p-6 max-w-md mx-auto">
      <div class="text-center mb-6">
        <i class="fas fa-check-circle text-green-500 text-5xl mb-3"></i>
        <h3 class="text-2xl font-bold text-gray-800">Order Confirmed</h3>
        <p class="text-gray-600">Thank you for your purchase!</p>
        <p class="text-sm text-gray-500 mt-2">Order #${orderId}</p>
      </div>

      ${addressHtml}

      <div class="mb-6">
        <h4 class="font-semibold text-indigo-700 mb-2">Order Items:</h4>
        ${itemsHtml}
      </div>

      <div class="flex justify-between items-center border-t border-gray-200 pt-4 mb-6">
        <span class="font-bold">Total</span>
        <span class="font-bold text-indigo-700">$${total.toFixed(2)}</span>
      </div>

      <div class="text-center">
        <button onclick="hideReceiptModal()" class="w-full bg-indigo-600 text-white rounded-full px-6 py-3 font-medium hover:bg-indigo-700 transition">
          Continue Shopping
        </button>
      </div>
    </div>
  `;

  const modal = document.createElement('div');
  modal.id = 'receipt-modal';
  modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
  modal.innerHTML = receiptHtml;
  document.body.appendChild(modal);
}

function hideReceiptModal() {
  const modal = document.getElementById('receipt-modal');
  if (modal) modal.remove();
}

// Testimonial functionality
const testimonials = [
  {
    content: "MyStore offers amazing products and excellent customer service. Highly recommended!",
    rating: 5,
    author: "Jane Doe"
  },
  {
    content: "I love the variety and quality of products. The delivery was fast and packaging was perfect.",
    rating: 4,
    author: "John Smith"
  },
  {
    content: "Great shopping experience! The website is easy to use and the prices are very competitive.",
    rating: 5,
    author: "Emily Johnson"
  }
];

let currentTestimonial = 0;

function showTestimonial(index) {
  const container = document.getElementById('testimonial-container');
  const testimonial = testimonials[index];

  container.innerHTML = `
    <div class="testimonial-slide">
      <p class="text-gray-700 italic mb-4">"${testimonial.content}"</p>
      <div class="flex items-center">
        <div class="flex">
          ${'<i class="fas fa-star text-yellow-400"></i>'.repeat(testimonial.rating)}
          ${'<i class="fas fa-star text-gray-300"></i>'.repeat(5 - testimonial.rating)}
        </div>
        <span class="ml-4 font-semibold text-indigo-700">${testimonial.author}</span>
      </div>
    </div>
  `;
}

document.getElementById('prevBtn')?.addEventListener('click', () => {
  currentTestimonial = (currentTestimonial - 1 + testimonials.length) % testimonials.length;
  showTestimonial(currentTestimonial);
});

document.getElementById('nextBtn')?.addEventListener('click', () => {
  currentTestimonial = (currentTestimonial + 1) % testimonials.length;
  showTestimonial(currentTestimonial);
});

// Initialize
showTestimonial(0);

// Question form
function submitQuestion(event) {
  event.preventDefault();
  const question = document.getElementById('questionInput').value.trim();

  if (!question) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Please enter your question',
      confirmButtonColor: '#6366f1',
    });
    return;
  }

  const phone = '6281329553000'; // Replace with your WhatsApp number
  const message = `Hello, I have a question: ${question}`;
  const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;

  window.open(whatsappUrl, '_blank');
  event.target.reset();
}

// Login simulation
document.getElementById('login-link')?.addEventListener('click', function(e) {
  e.preventDefault();
  Swal.fire({
    title: 'Login Form',
    html: `
      <input id="email" class="swal2-input" placeholder="Email">
      <input id="password" type="password" class="swal2-input" placeholder="Password">
    `,
    confirmButtonText: 'Login',
    focusConfirm: false,
    preConfirm: () => {
      const email = Swal.getPopup().querySelector('#email').value;
      const password = Swal.getPopup().querySelector('#password').value;

      if (!email || !password) {
        Swal.showValidationMessage('Please enter both email and password');
        return false;
      }

      return { email, password };
    }
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        icon: 'success',
        title: 'Logged in successfully!',
        showConfirmButton: false,
        timer: 1500
      });
      document.getElementById('login-link').textContent = 'LOGOUT';
    }
  });
});