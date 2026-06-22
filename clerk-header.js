(function(){
  var s = document.createElement("script");
  s.src = "https://firm-rodent-40.clerk.accounts.dev/npm/@clerk/clerk-js@latest/dist/clerk.browser.js";
  s.crossOrigin = "anonymous";
  s.dataset.clerkPublishableKey = "pk_test_ZmlybS1yb2RlbnQtNDAuY2xlcmsuYWNjb3VudHMuZGV2JA";
  s.async = true;
  document.head.appendChild(s);

  s.onload = function(){
    var c = window.Clerk;
    if (!c || typeof c.load !== "function") return;

    c.load().then(function(){
      var guest = document.getElementById("sh-guest");
      var user = document.getElementById("sh-user");
      if (!guest || !user) return;

      function update(u){
        if(u){
          guest.style.display = "none";
          user.style.display = "flex";
          var av = user.querySelector(".sh-user-avatar");
          var nm = user.querySelector(".sh-user-name");
          if(av) av.src = u.imageUrl || "";
          if(nm) nm.textContent = u.firstName || (u.emailAddresses && u.emailAddresses[0] ? u.emailAddresses[0].emailAddress.split("@")[0] : "");
        } else {
          guest.style.display = "";
          user.style.display = "none";
        }
      }

      update(c.user);
      c.addListener(function(ev){ update(ev.user); });

      var avatar = user.querySelector(".sh-user-avatar");
      if(avatar) avatar.addEventListener("click", function(){ c.openUserProfile(); });
    });
  };
})();
