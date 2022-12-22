# Serde Serialization Grammar

[Serde](https://serde.rs/) is a serialization framework based on the Rust language.

It defines a basic grammar of data tokens restricted by schemas that express a subset of the Rust type system.

Serialization is implemented by Serde codecs such as [bincode](./bincode.md).

## Grammar

### Data Grammar

The following EBNF-like grammar describes valid combinations of Serde tokens.

```ebnf
(* Root-level item *)
token ::= scalar | option | seq | enum | map ;

scalar ::= unit | bool | i8 | i16 | i32 | i64 | u8 | u16 | u32 | u64 | f32 | f64 ;

(* Optional value, e.g. `Option<T>`. *)
option ::= none | (some, token) ;

(* Constant-size array of tokens, e.g. `[u8; 32]`. *)
array ::= { token } ;

(* Struct of known tokens. *)
struct ::= { token } ;

(* Sequence of tokens of the same type, e.g. `Vec<T>`.
   `seq_length` indicates number of tokens that follow. *)
seq ::= seq_length, { token } ;

(* Switch between multiple types. e.g. `enum { x(...), y(...) }`.
   `enum_variant_tag` indicates type of token that follows. *)
enum ::= enum_variant_tag, token ;

(* Key-Value entry, e.g. BTreeMap<K, V>. Usually wrapped in a seq. *)
map_entry ::= token, token ;
map       ::= seq ;
```

### Data Schema Grammar

This specification uses the following subset of Rust to express schemas.

```ebnf
(* Root type *)
type ::= scalar | option_type | decl_struct_type | decl_enum_type | seq_type | array_type | map_type ;

(* Scalar types *)
unit   ::= "()" ;
scalar ::= unit | "bool" | "i8" | "i16" | "i32" | "i64" | "u8" | "u16" | "u32" | "u64" | "f32" | "f64" ;

(* Option type *)
option_type ::= "Option", "<", type, ">" ;

(* Struct type *)
decl_struct_type ::= "struct", identifier, ( struct_type_named | struct_type_tuple ) ;

struct_type_named ::= "{", { struct_type_field, [ ",", struct_type_field ] }, "}" ;
struct_type_field ::= identifier, ":", type ;

struct_type_tuple ::= "(", { type, [ ",", type ] }, ")" ;

(* Enum type *)
decl_enum_type ::= "enum", identifier, enum_type ;

enum_type    ::= "{", { enum_variant, [ ",", enum_variant ] }, "}" ;
enum_variant ::= identifier, { "(", type, ")" },  "," ;

(* Sequence type *)
seq_type     ::= vec_type | slice_type | str_type ;
vec_type     ::= "Vec", "<", type, ">" ;
slice_type   ::= "&", "[", vec_type, "]" ;
str_type     ::= str_ref_type | string_type ;
str_ref_type ::= "&", "str";
string_type  ::= "String" ;

(* Array type *)
array_type ::= "[", vec_type, ";", integer_literal "]" ;

(* Map type *)
map_type ::= "BTreeMap", "<", type, ",", type, ">" ;
```

### Constraints

The following constraints restrict the grammar of data tokens for a given schema.

Notation: `rust type = rust expression => serde tokens`.

#### Options

Options only serialize a value if the option tag is set to `some`.

- `Option<T> = None` => `none`
- `Option<T> = Some(t)` => `some, 't'`

#### Slices

Slices repeat items of the same type. The length is prefixed when serialized.

- `&[T] = &[t0, t1, ...]` => `'vec.len()' as seq_length, 't0', 't1', ...`
  - `Vec<T>` implicitly converted to `&[T]`
  - `&str` implicitly converted to `&[u8]` (UTF-8)
  - `String` implicitly converted to `&str`

#### Arrays

Arrays repeat items of the same type. The length is implied by the schema.

- `&[T; usize] = &[t0, t1, ...; n]` => `'n' as seq_length, 't0', 't1', ...`

#### Maps

Maps repeat key-value pairs of the same type. The length is prefixed when serialized.

Any `BTreeMap<K, V>` can be expressed by `&[(K, V)]`.
Most codecs mandate keys to be ordered ascending.

- `BTreeMap<K, V> = [(k0, v0), (k1, v1), ...].into()` => `'map.len()' as seq_length, 'k0', 'v0', 'k1', 'v1', ...`

#### Structs

Structs serialize each struct member in the same order as it appears in the struct.

- `struct _ (V0, V1, ...) = (v0, v1, ...)` => `'v0', 'v1', ...`
  - `struct _ { l0: V0, l1: V1, ... }` implicitly converted to ``struct _ (V0, V1, ...)`

#### Enums

Enums serialize one of the possible variants.
The variant tag is prefixed when serialized.
The variant tag is increases for every variant in the schema, starting with zero.

- `enum X { L0, L1(V1), ... } = X::L0` => `'0' as enum_variant_tag`
- `enum X { L0, L1(V1), ... } = X::L1(v1)` => `'1' as enum_variant_tag, v1`
