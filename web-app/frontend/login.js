let text = document.getElementById('login-form');
let sub = document.getElementById('login-form-submit');

function verify(user, pass) {
	//var user_session = sessionStorage.setItem("username", user);
	//var pass_session = sessionStorage.setItem("password", pass);
	data = {"user": user, "password": pass}
	fetch("http://127.0.0.1:5000/log_account", { method: "POST", mode: 'no-cors', body: JSON.stringify(data)}).then(results = resluts.json()).then(console.log)
	console.log(user + " as logged in.");
	
}

sub.addEventListener("click", (e) => {
    e.preventDefault();
    let user = text.username.value;
    let pass = text.password.value;

    verify(user, pass) 

})

//{ if (data["code"] === 201) {window.location.replace("http://localhost:5500/web-app/frontend/main_page.html")} else {console.log(data)}})