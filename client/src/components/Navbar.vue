<template>
  <nav class="navbar navbar-expand-sm navbar-light my-navbar my-3">
    <ul class="navbar-nav mr-auto">
      <li class="nav-item px-2" :class="{ active: current == 'home' }">
        <router-link class="nav-link" to="/">Home</router-link>
      </li>
      <li class="nav-item px-2" :class="{ active: current == 'about' }">
        <router-link class="nav-link" to="/about">About</router-link>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  props: {
    current: String,
  },
};
</script>

<style scoped>
.active {
  font-weight: bold;
}
.my-navbar {
  background-color: #dde9f0;
}
</style>