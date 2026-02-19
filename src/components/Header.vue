<template>
    <header class="navbar navbar-static-top max-w-3xl mx-auto" role="navigation">
        <div class="navbar-inner text-center">
            <img src="/Jazzcultural.jpeg" class="img-responsive w-[300px] mx-auto mb-4 mezzrow-logo">
            <ul class="nav nav-mezz navbar-nav flex gap-2 mx-auto mt-3 justify-between">
                <li class="active back">
                    <RouterLink to="/">Schedule</RouterLink>
                </li>
                <li>
                    <RouterLink to="/who-we-are">Who We Are</RouterLink>
                </li>
                <li>
                    <RouterLink to="/info">Info/Contact</RouterLink>
                </li>
                <li>
                    <RouterLink to="/reserve">Reserve</RouterLink>
                </li>
                <li>
                    <RouterLink to="/photos">Photos</RouterLink>
                </li>
                <li><a target="_blank" href="https://smallslive.com/" rel="external">SmallsLIVE</a></li>
            </ul>
        </div>
    </header>
</template>

<script setup>

</script>

<style>

.nav-mezz>li>a {
  border: 1px solid #F16722;
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
</style>