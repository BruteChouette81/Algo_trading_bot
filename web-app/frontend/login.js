let text = document.getElementById('login-form');
let sub = document.getElementById('login-form-submit');

function verify(user, pass, true_user, true_pass) {
	if (true_user.includes(user) && true_pass.includes(pass)) {
		window.location.replace("http://localhost:5500/web-app/frontend/main_page.html")
		var user_session = sessionStorage.setItem("username", user);
		var pass_session = sessionStorage.setItem("password", pass);
		data = {"user": user, "password": pass}
		fetch("http://127.0.0.1:5000/handle_account", { method: "POST", mode: 'no-cors', body: JSON.stringify(data)}).then(results => results.json()).then(console.log)
		console.log(user + " as logged in.")
	} else {
		alert("Password or Usrname incorrect...");
	}
}


var index = {"user": "Thomas", "pass": "douce123"}
let user_true = index["user"]
let pass_true = index["pass"]

sub.addEventListener("click", (e) => {
    e.preventDefault();
    let user = text.username.value;
    let pass = text.password.value;

    verify(user, pass, user_true, pass_true) 

})
