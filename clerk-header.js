(function(){
  var PK = "pk_test_ZmlybS1yb2RlbnQtNDAuY2xlcmsuYWNjb3VudHMuZGV2JA";
  var SIGNIN_URL = "https://locahun3d.com/sign-in";
  var SIGNUP_URL = "https://locahun3d.com/sign-up";

  // ── モバイルのドロワーにログイン導線を即時注入 ──
  // Clerk 未ロードでも redirect で機能するよう先に入れておく。
  function injectMobileAuth(){
    var nav = document.getElementById("mNav");
    if (!nav || document.getElementById("m-auth")) return;
    var box = document.createElement("div");
    box.id = "m-auth";
    box.style.cssText = "margin-top:auto;padding-top:18px;border-top:1px solid rgba(255,255,255,.15)";
    box.innerHTML =
      '<div id="m-guest">' +
        '<a id="m-signin" href="' + SIGNIN_URL + '">ログイン</a>' +
        '<a id="m-signup" href="' + SIGNUP_URL + '">新規登録</a>' +
      '</div>' +
      '<div id="m-user" style="display:none">' +
        '<a id="m-account" href="#">アカウント</a>' +
        '<a id="m-signout" href="#">ログアウト</a>' +
      '</div>';
    nav.appendChild(box);
  }
  if (document.readyState !== "loading") injectMobileAuth();
  else document.addEventListener("DOMContentLoaded", injectMobileAuth);

  // ── Clerk 本体をロード ──
  var s = document.createElement("script");
  s.src = "https://firm-rodent-40.clerk.accounts.dev/npm/@clerk/clerk-js@latest/dist/clerk.browser.js";
  s.crossOrigin = "anonymous";
  s.dataset.clerkPublishableKey = PK;
  s.async = true;
  document.head.appendChild(s);

  s.onload = function(){
    var c = window.Clerk;
    if (!c || typeof c.load !== "function") return;

    c.load().then(function(){
      injectMobileAuth();

      var guest = document.getElementById("sh-guest");
      var user  = document.getElementById("sh-user");
      var mGuest = document.getElementById("m-guest");
      var mUser  = document.getElementById("m-user");

      // ログイン/新規登録をその場のモーダルで開く（href はフォールバック）。
      function wireModal(el, fn){
        if (!el) return;
        el.addEventListener("click", function(e){
          if (window.Clerk && typeof window.Clerk[fn] === "function"){
            e.preventDefault();
            window.Clerk[fn]();
          }
        });
      }
      if (guest){
        var gA = guest.querySelectorAll("a");
        wireModal(gA[0], "openSignIn");   // ログイン
        wireModal(gA[1], "openSignUp");   // 新規登録
      }
      wireModal(document.getElementById("m-signin"), "openSignIn");
      wireModal(document.getElementById("m-signup"), "openSignUp");

      var mAccount = document.getElementById("m-account");
      if (mAccount) mAccount.addEventListener("click", function(e){ e.preventDefault(); c.openUserProfile(); });
      var mSignout = document.getElementById("m-signout");
      if (mSignout) mSignout.addEventListener("click", function(e){ e.preventDefault(); c.signOut(); });

      function update(u){
        if (u){
          if (guest) guest.style.display = "none";
          if (user)  user.style.display  = "flex";
          var av = user && user.querySelector(".sh-user-avatar");
          var nm = user && user.querySelector(".sh-user-name");
          if (av) av.src = u.imageUrl || "";
          if (nm) nm.textContent = u.firstName || (u.emailAddresses && u.emailAddresses[0] ? u.emailAddresses[0].emailAddress.split("@")[0] : "");
          if (mGuest) mGuest.style.display = "none";
          if (mUser)  mUser.style.display  = "block";
        } else {
          if (guest) guest.style.display = "";
          if (user)  user.style.display  = "none";
          if (mGuest) mGuest.style.display = "block";
          if (mUser)  mUser.style.display  = "none";
        }
      }

      update(c.user);
      c.addListener(function(ev){ update(ev.user); });

      var avatar = user && user.querySelector(".sh-user-avatar");
      if (avatar) avatar.addEventListener("click", function(){ c.openUserProfile(); });
    });
  };
})();
