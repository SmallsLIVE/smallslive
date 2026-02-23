<template>
    <header class="navbar navbar-static-top max-w-7xl mx-auto" role="navigation">
        <div class="navbar-inner text-center">
            <img src="/Jazzcultural.png" class="img-responsive w-[850px] h-[150px] mx-auto mb-4 mezzrow-logo p-4">
            <ul class="nav nav-mezz navbar-nav flex gap-2 mx-auto mt-3 justify-between">
                <li class="active back">
                    <RouterLink to="/"><img src="/navbar_images/schedule.png" class="img-responsive w-[150px] mx-auto mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li>
                    <RouterLink to="/reserve"><img src="/navbar_images/reserve.png" class="img-responsive w-[150px] mx-auto mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li>
                    <RouterLink to="/who-we-are"><img src="/navbar_images/who-we-are.png" class="img-responsive w-[150px] mx-auto mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li><RouterLink to="/smallslive"><img src="/navbar_images/smallslive.png" class="img-responsive w-[150px] mx-auto mb-4 mezzrow-logo"></RouterLink></li>
                <li>
                    <RouterLink to="/photos"><img src="/navbar_images/photos.png" class="img-responsive w-[150px] mx-auto mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li>
                    <RouterLink to="/info"><img src="/navbar_images/info.png" class="img-responsive w-[150px] mx-auto mb-4 mezzrow-logo"></RouterLink>
                </li>
            </ul>
        </div>
    </header>
</template>

<script setup>

</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@500;700&display=swap');

.nav-mezz>li>a {
  display: inline-block;
  font-size: 14px;
  font-weight: 700;
  color: #F16722;
  line-height: 22px;
  padding: 4px 15px;
  text-transform: uppercase;
  opacity: .8;

  &:hover {
    opacity: 1;
  }
}

.nav-mezz>li.active>a {
  opacity: 1;
}

@media  (max-width: 767px) {

  .navbar img {
    width: 100%;
  }

  .navbar-nav {
    flex-direction: column;
    padding: 0 15px;
  }

  .navbar-nav a {
    width: 100%;
  }

  .main-section {
    border: 0;
  }
}

.font-raleway {
  font-family: 'Raleway', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>