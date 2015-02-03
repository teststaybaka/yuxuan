function about_active() {
    var url = location.href.split('/')
    var side_nav;
    if (url[url.length-1] == 'about') {
        side_nav = document.getElementById('about');
    } else if (url[url.length-1] == 'contact') {
        side_nav = document.getElementById('contact');
    } else {
        side_nav = document.getElementById('hire_me');
    }
    side_nav.setAttribute('class', 'side active');
};

window.onload = function() {
    var url = location.href.split('/')
    var nav;
    if (url[url.length-1].indexOf('about') > -1) {
        nav = document.getElementById('about-nav');
        about_active();
    } else if (url[url.length-1].indexOf('projects') > -1) {
        nav = document.getElementById('projects-nav');
    } else if (url[url.length-1].indexOf('ideas') > -1) {
        nav = document.getElementById('ideas-nav');
    } else {
        nav = document.getElementById('home-nav');
    }
    nav.setAttribute('class', 'navigation active');
};