// ── Cart Storage ───────────────────────────────────────────
function getCart()       { return JSON.parse(localStorage.getItem('amenity_cart') || '[]'); }
function saveCart(cart)  { localStorage.setItem('amenity_cart', JSON.stringify(cart)); }

function updateBadge() {
  const total = getCart().reduce((s, i) => s + i.qty, 0);
  document.querySelectorAll('#cartBadge').forEach(b => b.textContent = total);
}

// ── Change Qty Input ───────────────────────────────────────
function changeQty(btn, delta) {
  const input = btn.parentElement.querySelector('.qty-input');
  input.value = Math.max(1, Math.min(20, parseInt(input.value) + delta));
}

// ── Add to Cart ────────────────────────────────────────────
function addToCart(id, name, price, btn) {
  const card  = btn.closest('.food-card');
  const input = card ? card.querySelector('.qty-input') : null;
  const qty   = input ? parseInt(input.value) : 1;
  const cart  = getCart();
  const idx   = cart.findIndex(i => i.id === id);
  if (idx >= 0) cart[idx].qty += qty;
  else          cart.push({ id, name, price, qty });
  saveCart(cart);
  updateBadge();
  showToast(`✓ ${name} added to cart!`, 'success');
}

// ── Get Alternatives ───────────────────────────────────────
async function getAlternatives(foodId, btn) {
  btn.disabled = true;
  btn.textContent = 'Loading...';
  try {
    const res  = await fetch(`/api/food/${foodId}`);
    const data = await res.json();
    const div  = document.getElementById(`alt-${foodId}`);
    div.innerHTML = '';
    if (!data.available) {
      if (data.alternatives && data.alternatives.length) {
        const label = document.createElement('p');
        label.style.cssText = 'font-size:.8rem;color:#d97706;margin-bottom:.4rem;font-weight:600;';
        label.textContent = '⚠️ Selected food is currently unavailable. Try:';
        div.appendChild(label);
        data.alternatives.forEach(alt => {
          const row = document.createElement('div');
          row.className = 'alt-item';
          row.innerHTML = `
            <span>${alt.name} – ₹${alt.price}</span>
            <button onclick="addToCart('${alt.id}','${alt.name}',${alt.price},this)">Add</button>`;
          div.appendChild(row);
        });
      } else {
        div.innerHTML = '<p style="font-size:.8rem;color:#888;margin-top:.4rem">No alternatives available right now.</p>';
      }
    }
  } catch (e) {
    console.error(e);
  }
  btn.disabled = false;
  btn.innerHTML = '<i class="fa fa-exchange-alt"></i> See Alternatives';
}

// ── Toast ──────────────────────────────────────────────────
function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.className   = 'toast ' + type + ' show';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 3000);
}

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', updateBadge);
