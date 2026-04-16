<template>
    <header class="navbar navbar-static-top max-w-7xl mx-auto" role="navigation">
        <div class="navbar-inner text-center">
            <RouterLink to="/"><img src="/Jazzcultural.png" class="img-responsive w-full h-auto md:w-[850px] md:h-[150px] mx-auto mb-4 mezzrow-logo p-4"></RouterLink>
            <ul class="nav nav-mezz navbar-nav flex gap-2 mx-auto mt-3 justify-between">
                <li class="back">
                    <RouterLink to="/"><img src="/navbar_images/schedule.png" class="img-responsive w-[150px] mx-auto mb-0 md:mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li>
                    <RouterLink to="/reserve"><img src="/navbar_images/reserve.png" class="img-responsive w-[150px] mx-auto mb-0 md:mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li>
                    <RouterLink to="/who-we-are"><img src="/navbar_images/who-we-are.png" class="img-responsive w-[150px] mx-auto mb-0 md:mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li><RouterLink to="/smallslive"><img src="/navbar_images/smallslive.png" class="img-responsive w-[150px] mx-auto mb-0 md:mb-4 mezzrow-logo"></RouterLink></li>
                <li>
                    <RouterLink to="/photos"><img src="/navbar_images/photos.png" class="img-responsive w-[150px] mx-auto mb-0 md:mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li>
                    <RouterLink to="/info"><img src="/navbar_images/info.png" class="img-responsive w-[150px] mx-auto mb-0 md:mb-4 mezzrow-logo"></RouterLink>
                </li>
                <li class="pt-1.5">
                    <RouterLink to="/newsletter">Newsletter</RouterLink>
                </li>
            </ul>
        </div>
    </header>
</template>

<script setup>

</script>

<style>

.nav-mezz>li>a {
  display: inline-block;
  font-size: 16px;
  font-weight: 700;
  /* color: #F16722; */
  color: white;
  line-height: 22px;
  padding: 4px 15px;
  text-transform: uppercase;
  opacity: .8;

  &:hover {
    opacity: 1;
  }
}

.nav-mezz>li>a.router-link-active {
  opacity: 1;
}

@media  (max-width: 767px) {

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

</style>