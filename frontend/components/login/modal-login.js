document.addEventListener("DOMContentLoaded", () => {
  // Declare todas as funções auxiliares antes de usá-las

  const getAccessToken = () => localStorage.getItem("access_token");

  const logout = () => {
    localStorage.removeItem("access_token");
    location.reload();
  };

  const loadModal = (url, containerId, callback) => {
    fetch(url)
      .then(response => response.text())
      .then(html => {
        const modalContainer = document.getElementById(containerId);
        modalContainer.innerHTML = html;
        setTimeout(callback, 100);
      });
  };

  const setupLogin = () => {
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;

      const response = await fetch("http://0.0.0.0:8000/auth/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("access_token", data.access_token);
        alert("Login bem-sucedido!");
        bootstrap.Modal.getInstance(document.getElementById("loginModal")).hide();
        location.reload();
      } else {
        alert("Erro no login!");
      }
    });
  };

  const setupRegister = () => {
    const registerButton = document.getElementById("registerButton");
    if (registerButton) {
      registerButton.addEventListener("click", async () => {
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const response = await fetch("http://0.0.0.0:8000/auth/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        if (response.ok) {
          alert("Usuário registrado com sucesso!");
        } else {
          const errorMsg = await response.text();
          alert("Erro ao registrar usuário: " + errorMsg);
        }
      });
    }
  };

  const setupAuth0 = () => {
    const auth0Button = document.getElementById("auth0Button");
    if (auth0Button) {
      auth0Button.addEventListener("click", () => {
        window.location.href =
          "https://YOUR_AUTH0_DOMAIN/authorize?" +
          "client_id=YOUR_AUTH0_CLIENT_ID" +
          "&redirect_uri=YOUR_CALLBACK_URL" +
          "&response_type=code" +
          "&scope=openid%20profile%20email" +
          "&connection=42";
      });
    }
  };

  // Agora, após declarar as funções, escolha qual modal carregar
  if (!getAccessToken()) {
    loadModal("/static/components/login/modal-login.html", "modal-login", () => {
      const loginModal = new bootstrap.Modal(document.getElementById("loginModal"));
      loginModal.show();
      setupLogin();
      setupRegister();
      setupAuth0();
    });
  } else {
    loadModal("/static/components/logout/modal-logout.html", "modal-logout", () => {
      const logoutModal = new bootstrap.Modal(document.getElementById("logoutModal"));
      logoutModal.show();
      const logoutButton = document.getElementById("logoutButton");
      if (logoutButton) {
        logoutButton.addEventListener("click", logout);
      }
    });
  }
});
