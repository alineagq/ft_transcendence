document.addEventListener("DOMContentLoaded", function () {
    if (!getAccessToken()) {
        fetch("/static/components/login/modal-login.html")
            .then(response => response.text())
            .then(html => {
                const modalContainer = document.getElementById("modal-login");
                modalContainer.innerHTML = html;

                setTimeout(() => {
                    const loginModal = new bootstrap.Modal(document.getElementById("loginModal"));
                    loginModal.show();
                    setupLogin();
                    setupRegister();
                }, 100);
            });
    } else {
        fetch("/static/components/logout/modal-logout.html")
            .then(response => response.text())
            .then(html => {
                const modalContainer = document.getElementById("modal-logout");
                modalContainer.innerHTML = html;
                console.log("HTML do modal de logout carregado:", html);

                setTimeout(() => {
                    const logoutModal = new bootstrap.Modal(document.getElementById("logoutModal"));
                    logoutModal.show();
                    const logoutButton = document.getElementById("logoutButton");
                    if (logoutButton) {
                        console.log("Botão de logout encontrado");
                        logoutButton.addEventListener("click", () => {
                            logout();
                        });
                    }
                }, 500);
            });


    }

    function setupLogin() {
        const form = document.getElementById("loginForm");
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            const response = await fetch("http://0.0.0.0:8000/auth/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                alert("Login bem-sucedido!");
                const loginModal = bootstrap.Modal.getInstance(document.getElementById("loginModal"));
                loginModal.hide();
                location.reload();
            } else {
                alert("Erro no login!");
            }
        });
    }

    function setupRegister() {
        const registerButton = document.getElementById("registerButton");
        if (registerButton) {
            registerButton.addEventListener("click", async () => {
                const username = document.getElementById("username").value;
                const password = document.getElementById("password").value;

                const response = await fetch("http://0.0.0.0:8000/auth/register/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    alert("Usuário registrado com sucesso!");
                } else {
                    let error_msg = await response.text();
                    alert("Erro ao registrar usuário: " + error_msg);
                }
            });
        }
    }

    async function refreshToken() {
        const refresh_token = localStorage.getItem("refresh_token");
        if (!refresh_token) return;

        const response = await fetch("http://0.0.0.0:8000/auth/refreshtoken/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refresh_token })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("access_token", data.access);
        } else {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
        }
    }

    function getAccessToken() {
        return localStorage.getItem("access_token");
    }

    function logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        location.reload();
    }
});
