document.addEventListener('DOMContentLoaded', function(){
  const loginForm = document.getElementById('loginForm');
  if (loginForm){
    loginForm.addEventListener('submit', async function(e){
      e.preventDefault();
      const line_id = document.getElementById('line_id').value.trim();
      const nickname = document.getElementById('nickname').value.trim();
      const msg = document.getElementById('msg');
      msg.innerText = '';
      if (!line_id){ msg.innerText = '請輸入 Line ID'; msg.style.color = 'red'; return; }
      const res = await fetch('/api/auth/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({line_id, nickname})});
      const data = await res.json();
      if (res.ok){
        localStorage.setItem('user', JSON.stringify(data));
        msg.innerText = '已登入：' + data.nickname + ' (id='+data.user_id+')';
        msg.style.color = 'green';
      } else {
        msg.innerText = data.error || '登入失敗';
        msg.style.color = 'red';
      }
    });
  }

  const applyForm = document.getElementById('applyForm');
  if (applyForm){
    applyForm.addEventListener('submit', async function(e){
      e.preventDefault();
      const title = document.getElementById('title').value.trim();
      const description = document.getElementById('description').value.trim();
      const side_pros = document.getElementById('side_pros').value.trim();
      const side_cons = document.getElementById('side_cons').value.trim();
      const created_by_raw = document.getElementById('created_by').value.trim();
      const resultEl = document.getElementById('result');
      resultEl.innerText = '';
      if (!title || !side_pros || !side_cons || !created_by_raw){ resultEl.innerText = '請填寫所有必填欄位'; resultEl.style.color='red'; return; }
      const created_by = parseInt(created_by_raw,10);
      if (isNaN(created_by)){ resultEl.innerText = '建立者欄位應為數字 user id'; resultEl.style.color='red'; return; }
      const payload = {title, description, side_pros, side_cons, rules:{}, is_public:true, created_by};
      const res = await fetch('/api/topics/apply', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      const data = await res.json();
      if (res.ok){
        resultEl.innerText = '已送出，topic_id=' + data.topic_id + ' 狀態=' + data.status;
        resultEl.style.color='green';
      } else {
        resultEl.innerText = '錯誤: ' + (data.error || JSON.stringify(data));
        resultEl.style.color='red';
      }
    });
  }
});
