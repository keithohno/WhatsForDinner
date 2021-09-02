<template>
  <div class="query-form">
    <div
      v-for="(ingredient, index) in ingredients"
      :key="index"
      class="input-group mb-1"
    >
      <input
        :value="ingredient"
        @input="(e) => edit_ingredient(index, e.target.value)"
        class="form-control"
      />
    </div>
    <div class="query-actions btn-group d-flex mb-4">
      <button class="btn btn-outline-secondary" @click="add_ingredient">
        ADD ITEM
      </button>
      <button class="btn btn-outline-secondary" @click="query">QUERY</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "QueryOptions",
  computed: {
    count() {
      return this.$store.state.count;
    },
    ingredients() {
      return this.$store.state.ingredients;
    },
  },
  methods: {
    add_ingredient() {
      this.$store.commit("add_ingredient", "");
    },
    edit_ingredient(index, value) {
      this.$store.commit("edit_ingredient", { index, value });
    },
    query() {
      this.$emit("query");
    },
  },
};
</script>

<style scoped>
.query-form {
  max-width: 500px;
}
</style>
