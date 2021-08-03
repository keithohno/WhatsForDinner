<template>
  <table class="table">
    <thead>
      <th scope="col">Name</th>
      <th scope="col">Amount</th>
      <th scope="col">Unit</th>
      <th scope="col">Modification</th>
    </thead>
    <tbody>
      <template v-for="(name, i) in names" :key="name">
        <Ingredient
          :name="name"
          :amount="amounts[i]"
          :unit="units[i]"
          :mod="mods[i]"
        />
      </template>
    </tbody>
  </table>
</template>

<script>
import Ingredient from "./Ingredient";
export default {
  name: "IngredientTable",
  props: {
    names: Array,
    amounts: Array,
    units: Array,
    mods: Array,
  },
  components: {
    Ingredient,
  },
};
</script>