<template>
  <div class="container mb-2">
    {{ recipe.name }}
    <button @click="togglehide">{{ shown ? "&lt;&lt;" : "&gt;&gt;" }}</button>
    <IngredientTable
      :names="recipe.ingredients"
      :amounts="recipe.amounts"
      :units="recipe.units"
      :mods="recipe.mods"
      v-if="shown"
    />
  </div>
</template>

<script>
import IngredientTable from "./IngredientTable.vue";
export default {
  name: "Recipe",
  data: () => {
    return {
      shown: false,
    };
  },
  methods: {
    togglehide() {
      this.shown = !this.shown;
    },
  },
  props: {
    recipe: Object,
  },
  components: {
    IngredientTable,
  },
};
</script>