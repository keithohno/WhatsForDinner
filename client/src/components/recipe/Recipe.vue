<template>
  <p>{{ recipe.name }}</p>
</template>

<script>
export default {
  name: "Recipe",
  props: {
    recipe: Object,
  },
};
</script>